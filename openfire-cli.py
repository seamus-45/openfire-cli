#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Openfire RestAPI command line interface
Usage:
    openfire-cli.py [--no-color] [--version] [--help] <module> [<args>...]

Options:
    --no-color          Supress color output
    -v, --version       Print version and exit
    -h, --help          Show this

Modules:
    users       List, add, update or delete users. Subscribe on groups. Manage lockouts and roster
    rooms       List, add, update or delete rooms. List room users or grant roles
    groups      List, add, update or delete groups
    sessions    List or close user sessions. View concurrent sessions
    system      List, add, update or delete system properties
    messages    Send broadcast message or get count of unread messages of the user

See 'openfire-cli.py <module> --help' for more information for a specific module.
"""
from docopt import (docopt, DocoptExit)
from codecs import getwriter
import sys
try:
    from config import (host, secret)
except:
    print('Error: config.py does not exists.')
    sys.exit(1)


__version__ = '0.0.1'


def rpr(data, indent=0, s='  '):
    """
    Print data objects
    """
    COLOR = '\033[92m' if color else ''
    DEFAULT = '\033[0m' if color else ''
    if type(data) is dict:
        for key, val in data.iteritems():
            if type(val) in [dict, list]:
                print(u'{i}{c}{key}{d}:'.format(i=indent*s, key=key, c=COLOR, d=DEFAULT))
                rpr(val, indent+1, s)
            else:
                print(u'{i}{c}{key}{d}: {val}'.format(i=indent*s, key=key, val=val, c=COLOR, d=DEFAULT))
    elif type(data) is list:
        for val in data:
            if type(val) in [dict, list]:
                rpr(val, indent, s)
                if indent == 1:
                    print
            else:
                print(u'{i}{val}'.format(i=indent*s, val=val))
    elif data is True:
        print('success')
    else:
        print(data)


def mod_users(argv): #noqa
    """
Usage:
    openfire-cli.py users --get <username>
    openfire-cli.py users --search [<query>]
    openfire-cli.py users --add <username> (--password=password | -W) [--name=name, --email=email]
    openfire-cli.py users --update <username> [--password=password | -W] [--name=name, --email=email]
    openfire-cli.py users --delete <username>
    openfire-cli.py users --lock <username>
    openfire-cli.py users --unlock <username>
    openfire-cli.py users --get-groups <username>
    openfire-cli.py users --add-groups <username> (--group=group)...
    openfire-cli.py users --delete-groups <username> (--group=group)...
    openfire-cli.py users --get-roster <username>
    openfire-cli.py users --add-roster-item <username> <jid> [--name=name --subscription=subscription] [--group=group]...
    openfire-cli.py users --update-roster-item <username> <jid> [--name=name --subscription=subscription] [--group=group]...
    openfire-cli.py users --delete-roster-item <username> <jid>
    openfire-cli.py users --help

Arguments:
    <username>                  The user name of the user
    <query>                     The search query. This act like the wildcard search %String%
    <jid>                       The jabber ID of the user

Commands:
    -g, --get                   View info about username
    -s, --search                List all users or search by query
    -a, --add                   Create a username
    -u, --update                Update a username
    -d, --delete                Delete a username
    -l, --lock                  Lock a username
    -L, --unlock                Unlock a username
    -G, --get-groups            View groups where username is a member
    -A, --add-groups            Add username to groups
    -D, --delete-groups         Delete a username from groups
    --get-roster                Get roster of the username
    --add-roster-item           Add roster item for username
    --update-roster-item        Update roster item for username
    --delete-roster-item        Delete roster item for username
    -h, --help                  Show this

Options:
    -p, --password=password     Specify password for username
    -W                          Prompt password from stdin
    -n, --name=name             The display name for the username
    -e, --email=email           The email address for the username
    --group=group               Add user to specified group. Can be specified multiple times
    --subscription=subscription Subscription of the user.
                                One of: remove, none, to, from, both. [default: both]
    """
    from ofrestapi import Users
    from getpass import getpass
    args = docopt(mod.__doc__, version=__version__, argv=argv)
    api = Users(host, secret)

    # map subscription types
    submap = {'remove': api.SUBSCRIPTION_REMOVE,
              'none': api.SUBSCRIPTION_NONE,
              'to': api.SUBSCRIPTION_TO,
              'from': api.SUBSCRIPTION_FROM,
              'both': api.SUBSCRIPTION_BOTH}
    try:
        args['--subscription'] = submap[args['--subscription']]
    except KeyError:
        print('Incorrect type of subscription: "{0}"'.format(args['--subscription']))
        raise DocoptExit

    # set password from stdin if requested
    if args['-W']:
        pwd = getpass('Please type password:')
        pwd_check = getpass('Please re-type password:')
        if pwd == pwd_check:
            args['--password'] = pwd
        else:
            exit('Passwords does not match')

    # actions
    if args['--add']:
        result = api.add_user(username=args['<username>'], password=args['--password'],
                              name=args['--name'], email=args['--email'])
    elif args['--update']:
        result = api.update_user(username=args['<username>'], password=args['--password'],
                                 name=args['--name'], email=args['--email'])
    elif args['--get']:
        user = api.get_user(args['<username>'])
        groups = api.get_user_groups(args['<username>'])
        result = user.copy()
        result.update(groups)
    elif args['--delete']:
        result = api.delete_user(args['<username>'])
    elif args['--search']:
        result = api.get_users(args['<query>'])
    elif args['--lock']:
        result = api.lock(args['<username>'])
    elif args['--unlock']:
        result = api.unlock(args['<username>'])
    elif args['--add-groups']:
        result = api.add_user_groups(username=args['<username>'], groups=args['--group'])
    elif args['--get-groups']:
        result = api.get_user_groups(args['<username>'])
    elif args['--delete-groups']:
        result = api.delete_user_groups(username=args['<username>'], groups=args['--group'])
    elif args['--get-roster']:
        result = api.get_user_roster(args['<username>'])
    elif args['--add-roster-item']:
        result = api.add_user_roster_item(username=args['<username>'], jid=args['<jid>'], name=args['--name'],
                                          subscription=args['--subscription'], groups=args['--group'])
    elif args['--update-roster-item']:
        result = api.update_user_roster_item(username=args['<username>'], jid=args['<jid>'], name=args['--name'],
                                             subscription=args['--subscription'], groups=args['--group'])
    elif args['--delete-roster-item']:
        result = api.delete_user_roster_item(username=args['<username>'], jid=args['<jid>'])
    rpr(result)


def mod_rooms(argv): #noqa
    """
Usage:
    openfire-cli.py rooms --get <room> [--service=service]
    openfire-cli.py rooms --search [<query>] [--type=type --service=service]
    openfire-cli.py rooms --who <room> [--service=service]
    openfire-cli.py rooms --add <room> --name=name --description=description [--service=service --subject=subject --max-users=n --temporary=y/n --private=y/n --hidden-jids=y/n --change-subject=y/n --any-can-invite=y/n --deny-registration=y/n --registered-nickname=y/n --deny-change-nickname=y/n --disable-log=y/n --members-only=y/n --moderated=y/n] [--broadcast=role]... [--owner=jid]... [--admin=jid]... [--member=jid]... [--outcast=jid...] [--password=password | -W]
    openfire-cli.py rooms --update <room> [--name=name --description=description --service=service --subject=subject --max-users=n --temporary=y/n --private=y/n --hidden-jids=y/n --change-subject=y/n --any-can-invite=y/n --deny-registration=y/n --registered-nickname=y/n --deny-change-nickname=y/n --disable-log=y/n --members-only=y/n --moderated=y/n] [--broadcast=role]... [--owner=jid]... [--admin=jid]... [--member=jid]... [--outcast=jid...] [--password=password | -W]
    openfire-cli.py rooms --delete <room> [--service=service]
    openfire-cli.py rooms --grant-role <room> <jid> <role> [--service=service]
    openfire-cli.py rooms --revoke-role <room> <jid> <role> [--service=service]
    openfire-cli.py rooms --help

Arguments:
    <room>                      The room name
    <query>                     The search query. This act like the wildcard search %String%
    <jid>                       The jabber ID of the user
    <role>                      One of: owners, admins, members, outcasts

Commands:
    -g, --get                   Get chat room info
    -s, --search                List all chat rooms or search by query
    -w, --who                   List chat room participants
    -a, --add                   Create a chat room
    -u, --update                Update a chat room
    -d, --delete                Delete a chat room
    --grant-role                Grant role to chat room user
    --revoke-role               Revoke role from chat room user
    -h, --help                  Show this

Options:
    -t, --type=type             Show only specified type of the rooms.
                                One of: all, public. [default: public]
    --service=service           The name of the Group Chat Service. [default: conference]
    -n, --name=name             Display name of the room, can contains non alphanumeric characters
    --description=description   Description text for the room
    --subject=subject           Subject of the room
    -p, --password=password     Password for the room
    -W                          Prompt password from stdin
    --max-users=n               The maximum number of occupants. '0' if unlimited
    --temporary=y/n             If True do not save room to database. Will be destroyed when the last occupant leave the room
    --private=y/n               If True make room not searchable through service discovery
    --hidden-jids=y/n           If True do not include the Jabber ID of every occupant in presence packets
    --change-subject=y/n        If True allow change subject by occupants
    --any-can-invite=y/n        If True occupants can invite other users in member only rooms
    --deny-registration=y/n     If True do not allow users to register with the room
    --registered-nickname=y/n   If True only join the room using registered nicknames
    --deny-change-nickname=y/n  If True do not allow occupants change their nicknames
    --disable-log=y/n           If True do not log room conversation
    --members-only=y/n          If True room requires an invitation to enter
    --moderated=y/n             If True only those with 'voice' may send messages to all occupants
    --broadcast=role            Role of which presence will be broadcasted to the rest of the occupants.
                                One of: moderator, participant, visitor.
                                Can be specified multiple times
    --owner=jid                 JID of the user with owner affiliation. Can be specified multiple times
    --admin=jid                 JID of the user with owner affiliation. Can be specified multiple times
    --member=jid                JID of the user with member affiliation. Can be specified multiple times
    --outcast=jid               JID of the user with outcast affiliation.
                                An outcast user is not allowed to join the room again.
                                Can be specified multiple times
    """
    from ofrestapi import Muc
    from getpass import getpass
    args = docopt(mod.__doc__, version=__version__, argv=argv)
    api = Muc(host, secret)

    # next block of code is exists because:
    # https://github.com/docopt/docopt/issues/51
    # opened ticket: https://github.com/docopt/docopt/issues/297
    for opt in '--temporary --private --hidden-jids --change-subject --any-can-invite --deny-registration --registered-nickname --deny-change-nickname --disable-log --members-only --moderated'.split():
        if args[opt]:
            if args[opt].lower() in 'true y yes 1'.split():
                args[opt] = True
            elif args[opt].lower() in 'false n no 0'.split():
                args[opt] = False
            else:
                raise DocoptExit()

    # set password from stdin if requested
    if args['-W']:
        pwd = getpass('Please type room password:')
        pwd_check = getpass('Please re-type room password:')
        if pwd == pwd_check:
            args['--password'] = pwd
        else:
            exit('Passwords does not match')

    # actions
    if args['--get']:
        result = api.get_room(roomname=args['<room>'], servicename=args['--service'])
    elif args['--search']:
        result = api.get_rooms(servicename=args['--service'], typeof=args['--type'], query=args['<query>'])
    elif args['--who']:
        result = api.get_room_users(roomname=args['<room>'], servicename=args['--service'])
    elif args['--add']:
        result = api.add_room(roomname=args['<room>'], name=args['--name'], description=args['--description'],
                              servicename=args['--service'], subject=args['--subject'], password=args['--password'],
                              maxusers=args['--max-users'], changesubject=args['--change-subject'],
                              anycaninvite=args['--any-can-invite'], membersonly=args['--members-only'],
                              moderated=args['--moderated'], broadcastroles=args['--broadcast'],
                              owners=args['--owner'], admins=args['--admin'], members=args['--member'],
                              registerednickname=args['--registered-nickname'], outcasts=args['--outcast'],
                              persistent=False if args['--temporary'] else True,
                              public=False if args['--private'] else True,
                              registration=False if args['--deny-registration'] else True,
                              visiblejids=False if args['--hidden-jids'] else True,
                              changenickname=False if args['--deny-change-nickname'] else True,
                              logenabled=False if args['--disable-log'] else True)
    elif args['--update']:
        # gather old settings
        old = api.get_room(roomname=args['<room>'], servicename=args['--service'])
        # prevent KeyError exception
        old['broadcastPresenceRoles'] = old['broadcastPresenceRoles']['broadcastPresenceRole'] if old['broadcastPresenceRoles'] else None
        old['owners'] = old['owners']['owner'] if old['owners'] else None
        old['admins'] = old['admins']['admin'] if old['admins'] else None
        old['members'] = old['members']['member'] if old['members'] else None
        old['outcasts'] = old['outcasts']['outcast'] if old['outcasts'] else None
        if 'password' not in old.keys():
            old['password'] = None
        # finally
        result = api.update_room(roomname=args['<room>'],
                                 servicename=args['--service'],
                                 name=old['naturalName'] if args['--name'] is None else args['--name'],
                                 description=old['description'] if args['--description'] is None else args['--description'],
                                 subject=old['subject'] if args['--subject'] is None else args['--subject'],
                                 password=old['password'] if args['--password'] is None else args['--password'],
                                 maxusers=old['maxUsers'] if args['--max-users'] is None else args['--max-users'],
                                 persistent=old['persistent'] if args['--temporary'] is None else not args['--temporary'],
                                 public=old['publicRoom'] if args['--private'] is None else not args['--private'],
                                 registration=old['registrationEnabled'] if args['--deny-registration'] is None else not args['--deny-registration'],
                                 visiblejids=old['canAnyoneDiscoverJID'] if args['--hidden-jids'] is None else not args['--hidden-jids'],
                                 changesubject=old['canOccupantsChangeSubject'] if args['--change-subject'] is None else args['--change-subject'],
                                 anycaninvite=old['canOccupantsInvite'] if args['--any-can-invite'] is None else args['--any-can-invite'],
                                 changenickname=old['canChangeNickname'] if args['--deny-change-nickname'] is None else not args['--deny-change-nickname'],
                                 logenabled=old['logEnabled'] if args['--disable-log'] is None else not args['--disable-log'],
                                 registerednickname=old['loginRestrictedToNickname'] if args['--registered-nickname'] is None else args['--registered-nickname'],
                                 membersonly=old['membersOnly'] if args['--members-only'] is None else args['--members-only'],
                                 moderated=old['moderated'] if args['--moderated'] is None else args['--moderated'],
                                 broadcastroles=old['broadcastPresenceRoles'] if args['--broadcast'] is None else args['--broadcast'],
                                 owners=old['owners'] if args['--owner'] is None else args['--owner'],
                                 admins=old['admins'] if args['--admin'] is None else args['--admin'],
                                 members=old['members'] if args['--member'] is None else args['--member'],
                                 outcasts=old['outcasts'] if args['--outcast'] is None else args['--outcast'])
    elif args['--delete']:
        result = api.delete_room(roomname=args['<room>'], servicename=args['--service'])
    elif args['--grant-role']:
        result = api.grant_user_role(roomname=args['<room>'], servicename=args['--service'],
                                     username=args['<jid>'], role=args['<role>'])
    elif args['--revoke-role']:
        result = api.revoke_user_role(roomname=args['<room>'], servicename=args['--service'],
                                      username=args['<jid>'], role=args['<role>'])

    rpr(result)


def mod_groups(argv):
    """
Usage:
    openfire-cli.py groups --get <group>
    openfire-cli.py groups --list
    openfire-cli.py groups --add <group> <description>
    openfire-cli.py groups --update <group> <description>
    openfire-cli.py groups --delete <group>

Arguments:
    <group>                     The name of group
    <description>               Description of the group

Commands:
    -g, --get                   Get group info
    -l, --list                  List all groups
    -a, --add                   Create group
    -u, --update                Update group
    -d, --delete                Delete group
    -h, --help                  Show this
    """
    from ofrestapi import Groups
    args = docopt(mod.__doc__, version=__version__, argv=argv)
    api = Groups(host, secret)
    # actions
    if args['--get']:
        result = api.get_group(args['<group>'])
    elif args['--list']:
        result = api.get_groups()
    elif args['--add']:
        result = api.add_group(args['<group>'], args['<description>'])
    elif args['--update']:
        result = api.update_group(args['<group>'], args['<description>'])
    elif args['--delete']:
        result = api.delete_group(args['<group>'])
    rpr(result)


def mod_sessions(argv):
    """
Usage:
    openfire-cli.py sessions --list
    openfire-cli.py sessions --get <username>
    openfire-cli.py sessions --close <username>
    openfire-cli.py sessions --concurrent

Arguments:
    <username>              The user name of the user or JID

Commands:
    -l, --list          List all sessions
    -g, --get           Get user sessions
    -c, --close         Close user sessions
    --concurrent        Get concurrent cluster or local sessions
    -h, --help          Show this
    """
    from ofrestapi import (Sessions, System)
    args = docopt(mod.__doc__, version=__version__, argv=argv)
    api = Sessions(host, secret)
    # actions
    if args['--list']:
        result = api.get_sessions()
    elif args['--get']:
        result = api.get_user_sessions(args['<username>'])
    elif args['--close']:
        result = api.close_user_sessions(args['<username>'])
    elif args['--concurrent']:
        api = System(host, secret)
        result = api.get_concurrent_sessions()
    rpr(result)


def mod_system(argv):
    """
Usage:
    openfire-cli.py system --list
    openfire-cli.py system --get <key>
    openfire-cli.py system --update <key> <value>
    openfire-cli.py system --delete <key>

Arguments:
    <key>               Key of the property
    <value>             Value of the property

Commands:
    -l, --list          List all system properties
    -g, --get           Get system property
    -u, --update        Update system property
    -d, --delete        Delete system property
    -h, --help          Show this
    """
    from ofrestapi import System
    args = docopt(mod.__doc__, version=__version__, argv=argv)
    api = System(host, secret)
    # actions
    if args['--list']:
        result = api.get_props()
    elif args['--get']:
        result = api.get_prop(args['<key>'])
    elif args['--update']:
        result = api.update_prop(args['<key>'], args['<value>'])
    elif args['--delete']:
        result = api.delete_prop(args['<key>'])
    rpr(result)


def mod_messages(argv):
    """
Usage:
    openfire-cli.py messages --send <message>
    openfire-cli.py messages --unread <jid>

Arguments:
    <message>           Message text to be send
    <jid>               Jabber ID of the user

Commands:
    -s, --send          Send a broadcast message to all online users
    -u, --unread        Get unread messages count
    -h, --help          Show this

    """
    from ofrestapi import Messages
    args = docopt(mod.__doc__, version=__version__, argv=argv)
    api = Messages(host, secret)
    # actions
    if args['--send']:
        result = api.send_broadcast(args['<message>'])
    elif args['--unread']:
        result = api.get_unread_messages(args['<jid>'])
    rpr(result)


if __name__ == '__main__':
    # make encoding forced for pipe
    if sys.stdout.encoding != 'UTF-8':
        sys.stdout = getwriter('utf-8')(sys.stdout, 'strict')
    # parse arguments
    args = docopt(__doc__, version=__version__, options_first=True)
    argv = [args['<module>']] + args['<args>']
    color = False if args['--no-color'] else True
    if args['<module>'] in 'users rooms groups sessions system messages'.split():
            mod_name = 'mod_{0}'.format(args['<module>'])
            mod = locals()[mod_name]
            try:
                mod(argv)
            except Exception as e:
                print('{0}: {1}'.format(type(e).__name__, e.args[0]))
    else:
        exit("'{0}' is not a openfire-cli.py module. See 'openfire-cli.py --help'.".format(args['<module>']))
