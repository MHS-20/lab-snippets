from .example3_rpc_client import *
import argparse
import sys

# estendere user_db, deve prendere il token in input ed inviarlo al server
# in realtà già lo mandi il token, solo che lo carichi nel client al momento della creazione
# devi aggiornare il campo token in client stub dopo che ti sei autenticato? 
# in realtà no perché dovrebbe leggerlo da file appena scritto

# C'è un problema lato server nel fare il marshalling del token


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog=f'python -m snippets -l 4 -e 4',
        description='RPC client for user database',
        exit_on_error=False,
    )
    
    parser.add_argument('address', help='Server address in the form ip:port')
    parser.add_argument('command', help='Method to call', choices=['add', 'get', 'check', 'authenticate', 'validate'])
    parser.add_argument('--user', '-u', help='Username')
    parser.add_argument('--email', '--address', '-a', nargs='+', help='Email address')
    parser.add_argument('--name', '-n', help='Full name')
    parser.add_argument('--role', '-r', help='Role (defaults to "user")', choices=['admin', 'user'])
    parser.add_argument('--password', '-p', help='Password')

    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        parser.print_help()
        sys.exit(0)

    args.address = address(args.address)
    user_db = RemoteUserDatabase(args.address)
    auth_service = RemoteAuthenticationService(args.address)

    try :
        ids = (args.email or []) + [args.user]
        if len(ids) == 0:
            raise ValueError("Username or email address is required")
        match args.command:
            case 'add':
                if not args.password:
                    raise ValueError("Password is required")
                if not args.name:
                    raise ValueError("Full name is required")
                user = User(args.user, args.email, args.name, Role[args.role.upper()], args.password)
                print(user_db.add_user(user))
            
            case 'get':
                print(user_db.get_user(ids[0])) 
            
            case 'check':
                credentials = Credentials(ids[0], args.password)
                print(user_db.check_password(credentials))
            
            case 'authenticate':
                credentials = Credentials(args.user, args.password)
                auth_service.token = auth_service.authenticate(credentials)
                print("Token: ", auth_service.token)
                auth_service.store_token(auth_service.token)
            
            case 'validate':
                print(auth_service.validate_token(auth_service.token)) # send validation request
            
            case _:
                raise ValueError(f"Invalid command '{args.command}'")
    except RuntimeError as e:
        print(f'[{type(e).__name__}]', *e.args)
