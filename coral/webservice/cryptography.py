import sys
import gnupg
import uuid


# TODO: consider passphrase, handle exceptions
class Cryptography(object):
    def __init__(self):
        sys.stdout.write('Initialising cryptography manager... ')
        self._coral_keyring = gnupg.GPG(gnupghome='./coral_keyring')
        self._client_keyring = gnupg.GPG(gnupghome='./client_keyring')

        # If coral keyring is empty
        if len(self._coral_keyring.list_keys()) == 0:
            self._generate_keys()

        # Coral keys management
        key_id = self._coral_keyring.list_keys()[0]['keyid']
        self._public_key = self._coral_keyring.export_keys(key_id)
        self._private_fingerprint = self._coral_keyring.list_keys(secret=True)[0]['fingerprint']

        # Deletes all keys from client keyring
        client_fingerprints = [k['fingerprint'] for k in self._client_keyring.list_keys()]
        if len(client_fingerprints) == 0:
            self._client_keyring.delete_keys(client_fingerprints)

        self._client_fingerprint_dict = {}

        print 'OK'

    def _generate_keys(self):
        """
        Generates Coral's keys
        """
        key_params = {
            'name_real': 'Coral',
            'key_type': 'RSA',
            'key_length': 4096
        }
        self._coral_keyring.encoding = 'utf-8'
        key_input = self._coral_keyring.gen_key_input(**key_params)
        self._coral_keyring.gen_key(key_input)

    def get_coral_key(self):
        """
        Gets the Coral's public key
        """
        return self._public_key

    def register_client_key(self, client_key):
        """
        Adds a public key received from a client to clients' keyring
        """
        client_id = str(uuid.uuid1())
        import_result = self._client_keyring.import_keys(client_key)

        if len(import_result.fingerprints) == 0:
            raise Exception('Invalid client key.')

        self._client_fingerprint_dict[client_id] = import_result.fingerprints[0]
        return client_id

    def remove_client_key(self, client_id):
        """
        Removes a public key which is assigned to some client from client's keyring
        """
        if client_id in self._client_fingerprint_dict:
            self._client_keyring.delete_keys([self._client_fingerprint_dict[client_id]])
            del self._client_fingerprint_dict[client_id]

    def encrypt(self, client_id, message):
        """
        Encrypts an outbound message using a public key which is assigned to some client
        """
        client_fingerprint = self._client_fingerprint_dict[client_id]
        return self._client_keyring.encrypt(message, client_fingerprint, always_trust=True)

    def decrypt(self, message):
        """
        Decrypts an inbound message using the Coral's private key
        """
        return self._coral_keyring.decrypt(message)
