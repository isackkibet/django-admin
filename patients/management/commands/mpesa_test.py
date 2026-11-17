from django.conf import settings
from django.core.management.base import BaseCommand

from django_daraja.mpesa.core import MpesaClient
from django_daraja.mpesa.exceptions import MpesaError
from django_daraja.mpesa.utils import generate_access_token_request


class Command(BaseCommand):
    help = (
        'Test the M-Pesa Daraja sandbox settings by requesting an OAuth token '
        'and (optionally) sending an STK push to the sandbox test number.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--phone', default=None, help='Phone number to receive the STK prompt.')
        parser.add_argument('--amount', type=int, default=1, help='Whole-number amount to request.')
        parser.add_argument('--skip-stk', action='store_true', help='Only test OAuth authentication.')
        parser.add_argument('--b2c', action='store_true', help='Test a B2C BusinessPayment request.')

    def handle(self, *args, **options):
        self.stdout.write('M-Pesa configuration:')
        self.stdout.write(f'  environment       = {settings.MPESA_ENVIRONMENT}')
        self.stdout.write(f'  shortcode (B2C)   = {settings.MPESA_SHORTCODE}')
        self.stdout.write(f'  express shortcode = {settings.MPESA_EXPRESS_SHORTCODE}')
        self.stdout.write(f'  passkey           = {self._mask(settings.MPESA_PASSKEY)}')
        self.stdout.write(f'  consumer key      = {self._mask(settings.MPESA_CONSUMER_KEY)}')
        self.stdout.write(f'  consumer secret   = {self._mask(settings.MPESA_CONSUMER_SECRET)}')
        self.stdout.write(f'  initiator name    = {settings.MPESA_INITIATOR_USERNAME}')
        self.stdout.write(f'  callback URL      = {settings.MPESA_CALLBACK_URL or "(not set)"}')

        missing = [
            name
            for name in ('MPESA_CONSUMER_KEY', 'MPESA_CONSUMER_SECRET')
            if not getattr(settings, name)
        ]
        if missing:
            self.stderr.write(
                'Missing required settings: ' + ', '.join(missing)
                + '. Add the Consumer Key and Consumer Secret of your Daraja app.'
            )
            return

        self.stdout.write('\n[1/3] Requesting OAuth access token...')
        response = generate_access_token_request()
        if response.status_code != 200:
            self.stderr.write(
                f'Authentication failed (HTTP {response.status_code}): {response.text[:300]}'
            )
            return
        self.stdout.write(self.style.SUCCESS('Authentication OK.'))

        if options['skip_stk'] and not options['b2c']:
            self.stdout.write('\nOAuth test passed.')
            return

        phone = options['phone'] or settings.MPESA_TEST_PHONE
        client = MpesaClient()

        if not options['b2c']:
            self.stdout.write(f'\n[2/3] Sending STK push to {phone}...')
            if not settings.MPESA_CALLBACK_URL:
                self.stderr.write(
                    'MPESA_CALLBACK_URL is not set. Safaricom requires a public HTTPS URL '
                    'to receive the STK result.'
                )
                return
            try:
                result = client.stk_push(
                    phone,
                    options['amount'],
                    'Hospital Payment',
                    'Hospital services',
                    settings.MPESA_CALLBACK_URL,
                )
            except MpesaError as exc:
                self.stderr.write(f'STK push failed: {exc}')
                return
            self.stdout.write(
                f'  response_code        = {result.response_code}\n'
                f'  response_description = {result.response_description}\n'
                f'  checkout_request_id  = {result.checkout_request_id}'
            )
            if str(result.response_code) == '0':
                self.stdout.write(self.style.SUCCESS('STK push accepted. Check the phone.'))
            else:
                self.stderr.write('STK push was rejected.')
            return

        self.stdout.write(f'\n[2/3] Sending B2C BusinessPayment to {phone}...')
        try:
            result = client.business_payment(
                phone,
                options['amount'],
                'Hospital Payment',
                settings.MPESA_CALLBACK_URL,
                'Hospital services',
            )
        except MpesaError as exc:
            self.stderr.write(f'B2C payment failed: {exc}')
            return
        self.stdout.write(
            f'  response_code        = {result.response_code}\n'
            f'  response_description = {result.response_description}\n'
            f'  conversation_id      = {result.conversation_id}'
        )
        if str(result.response_code) == '0':
            self.stdout.write(self.style.SUCCESS('B2C payment accepted.'))
        else:
            self.stderr.write('B2C payment was rejected.')

    @staticmethod
    def _mask(value):
        if not value:
            return '(not set)'
        if len(value) <= 6:
            return '*' * len(value)
        return f'{value[:3]}...{value[-3:]}'
