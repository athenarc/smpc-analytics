import argparse
import sys
import json
import getpass
import os
from subprocess import Popen, PIPE, STDOUT
from huepy import *
import hashlib

class ProcessError(Exception):
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message

def execute(command, stdout, stdin, stderr, verbose=False):
    if verbose:
        # print('[INFO] Running: ' + ' '.join(command))
        print(run('Running: ' + ' '.join(command)))
    process = Popen(command, stdout=stdout, stdin = stdin, stderr = stderr)
    out, err = process.communicate();
    rc = process.returncode
    if rc != 0:
        if verbose:
            print(out)
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
    parser.add_argument('--verbose', help = 'See executed commands in verbose output', action = 'store_true')
    parser.add_argument('--install', help = 'Set this flag if you wish the public key to be installed into the SMPC cluster', action = 'store_true')
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
        execute(["openssl", "req", "-x509", "-config", "openssl.cnf", "-extensions", "ext", "-subj", subj, "-days", str(args.days), "-nodes", "-newkey", "rsa:"+str(args.size), "-keyout", private_key, "-out", public_key, "-outform", "der"], stdout=PIPE, stdin=PIPE, stderr=STDOUT, verbose=args.verbose)
    except ProcessError as e:
        print(bad('Error in key generation'))
        return 1
    try:
        execute(["openssl", "rsa", "-in", private_key, "-out", private_key, "-outform", "der"], stdout=PIPE, stdin=PIPE, stderr=STDOUT, verbose=args.verbose)
    except ProcessError as e:
        print(bad('Error in key generation'))
        return 1

    print(good("Keys " + public_key + " and " + private_key + " generated successfully."))

    with open(ascii_public_key, 'w') as ascii_file:
        command = ["openssl", "x509", "-text", "-noout", "-inform", "der", "-in", public_key]
        try:
            execute(command, stdout=ascii_file, stdin=PIPE, stderr=STDOUT, verbose=args.verbose)
        except ProcessError as e:
            print(bad('Error in key generation'))
            return 1
        print(good("Ascii version of " + public_key + " located at " + ascii_public_key ))

    if args.install:
        smpc_servers = json.load(open('smpc_servers.json'))
        servers = smpc_servers['servers']
        users = smpc_servers['users']
        local_user = getpass.getuser()
        remote_user = users[local_user]
        for server,ip in servers.items():
            try:
                execute(['sshpass', '-f', '/home/'+local_user+'/.p', 'scp', public_key, remote_user+'@'+ip+':/etc/sharemind/'  ], stdout=PIPE, stdin=PIPE, stderr=STDOUT, verbose=args.verbose)
            except ProcessError as e:
                print(bad('Error copying key at server '+server))
                return 1
            try:
                execute(['sshpass', '-f', '/home/'+local_user+'/.p', 'ssh', remote_user+'@'+ip, 'echo', '"'+public_key+': import-script.sb'+'" >> /etc/sharemind/server-whitelist.conf'], stdout=PIPE, stdin=PIPE, stderr=STDOUT, verbose=args.verbose)
            except ProcessError as e:
                print(bad('Error copying key at server '+server))
                return 1
        print(good('Public key ' + public_key + ' successfully installed in all SMPC servers'))

    if os.path.isfile('generated_keys.json'):
        generated_keys = json.load(open('generated_keys.json'))
    else:
        generated_keys = {}
    key_hash = hashlib.sha256(open(public_key).readline()).hexdigest()
    if args.CommonName in generated_keys:
        generated_keys[args.CommonName].append({'name' : public_key, 'hash' : key_hash})
    else:
        generated_keys[args.CommonName] = [{'name' : public_key, 'hash' : key_hash}]

    with open('generated_keys.json', 'w') as outfile:
        json.dump(generated_keys, outfile)

    if args.verbose:
        print(info('Public key for ' + args.CommonName + ' is ' + public_key ))
        print(info('Hash: ' + hashlib.sha256(open(public_key).readline()).hexdigest()))


if __name__ == '__main__':
    main()
