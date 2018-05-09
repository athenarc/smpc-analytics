import argparse
import sys
from subprocess import Popen, PIPE, STDOUT

class ProcessError(Exception):
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message

def execute(command, stdout, stdin, stderr, verbose=False):
    if verbose:
        print('[INFO] Running: ' + ' '.join(command))
    process = Popen(command, stdout=stdout, stdin = stdin, stderr = stderr)
    out, err = process.communicate();
    rc = process.returncode
    if rc != 0:
        raise ProcessError()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('CommonName', help = 'Common Name [CN] of the client that the keys will be generated for')
    parser.add_argument('--CountryName', help = 'Country Name [C] (2 letter code) of the client that the keys will be generated for')
    parser.add_argument('--State', help = 'State or Province Name [ST] (full name) of the client that the keys will be generated for')
    parser.add_argument('--LocalityName', help = 'Locality Name [L] (eg, city) of the client that the keys will be generated for')
    parser.add_argument('--OrganizationName', help = 'Organization Name [O] (eg, company) of the client that the keys will be generated for')
    parser.add_argument('--OrganizationUnit', help = 'Organization Unit [OU] (eg, section) of the client that the keys will be generated for')
    parser.add_argument('--EmailAddress', help = 'Email address [emailAddress] of the client that the keys will be generated for')
    parser.add_argument('--days', help = 'Number of days that the certificate should be valid', default = 365, type = int)
    parser.add_argument('--size', help = 'Size of the RSA keys in bits', default = 2048, type = int)
    args = parser.parse_args()

    subj = ''
    if args.CountryName != None:
        subj += '/C='+args.CountryName
    if args.State != None:
        subj += '/ST='+args.State
    if args.LocalityName != None:
        subj += '/L='+args.LocalityName
    if args.OrganizationName != None:
        subj += '/O='+args.OrganizationName
    if args.OrganizationUnit != None:
        subj += '/O='+args.OrganizationUnit
    subj += '/CN='+args.CommonName
    if args.EmailAddress != None:
        subj += '/emailAddress='+args.EmailAddress

    private_key = args.CommonName + '-private-key'
    public_key = args.CommonName + '-public-key'
    ascii_public_key = args.CommonName + '-public-key-ascii'
    try:
        execute(["openssl", "req", "-x509", "-config", "openssl.cnf", "-extensions", "ext", "-subj", subj, "-days", str(args.days), "-nodes", "-newkey", "rsa:"+str(args.size), "-keyout", private_key, "-out", public_key, "-outform", "der"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    except ProcessError as e:
        print('Error in key generation')
        return 1
    try:
        execute(["openssl", "rsa", "-in", private_key, "-out", private_key, "-outform", "der"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    except ProcessError as e:
        print('Error in key generation')
        return 1

    print("Keys " + public_key + " and " + private_key + " generated successfully.")

    with open(ascii_public_key, 'w') as ascii_file:
        command = ["openssl", "x509", "-text", "-noout", "-inform", "der", "-in", public_key]
        try:
            execute(command, stdout=ascii_file, stdin=PIPE, stderr=STDOUT)
        except ProcessError as e:
            print('Error in key generation')
            return 1
        print("Ascii version of " + private_key + " located at " + ascii_public_key )


if __name__ == '__main__':
    main()
