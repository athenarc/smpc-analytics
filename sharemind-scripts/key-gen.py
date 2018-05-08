import argparse
from subprocess import Popen, PIPE, STDOUT

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('client', help = 'Common Name [CN] of the client that the keys will be generated for')
    parser.add_argument('--days', help = 'Number of days that the certificate should be valid', default = 365, type=int)
    parser.add_argument('--size', help = 'Size of the RSA keys in bits', default = 2048, type=int)
    args = parser.parse_args()
    input = '.\n'*5 + args.client + '\n.\n' # Set Common Name [CN], leave rest blank.
    public_key = args.client + '-public-key'
    private_key = args.client + '-private-key'
    openssl = Popen(["openssl", "req", "-x509", "-days", str(args.days), "-nodes", "-newkey", "rsa:"+str(args.size), "-keyout", private_key, "-out", public_key, "-outform", "der"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    out, err = openssl.communicate(input=input)
    rc = openssl.returncode
    if rc == 0:
        print("Keys generated successfully.")
    else:
        print("Error in key generation")
        return 1



if __name__ == '__main__':
    main()
