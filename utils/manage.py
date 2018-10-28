#!/usr/bin/env python

import sys
import os
import random
import string

from Crypto.PublicKey import RSA

def generate_rsa_key_pair(length=2048):
    key = RSA.generate(length)
    private_key = key.exportKey()
    public_key = key.publickey().exportKey()
    return str(public_key), str(private_key)

def random_string(length=0x10):
    charset = string.letters + string.digits
    return "".join([random.choice(charset) for i in range(length)])

class Manager(object):
    def __init__(self, playground, template):
        self.playground = playground
        self.template = template

    def create_team(self):
        '''
        Create team
            create_team src dst
        '''
        # Assign team id
        team_id = self.count_team()
        team_folder = "%s/%d" % (self.playground, team_id)
        print("Assigned team id: %d" % (team_id))
        # Assign access cred
        ctf_password = random_string(0x10)
        root_password = random_string(0x10)
        public_key, private_key = generate_rsa_key_pair()
        # Assign IP address
        subnet = "172.100.1.0/16"
        gateway = "172.100.1.1"
        ip = "%s.%d" % (subnet.split(".0/")[0], team_id)
        # Assign ports
        service_port = team_id * 5
        ssh_port = team_id * 5 + 1
        config = {
            # Common
            "team_id": team_id,
            "team_folder":team_folder,
            # Auth
            "ctf_password":ctf_password,
            "root_password":root_password,
            "public_key":public_key,
            "private_key":private_key,
            # Net
            "subnet" :subnet,
            "gateway":gateway,
            "ip":ip,
            # Service
            "service_port":service_port,
            "ssh_port":ssh_port,
        }
        # Create team folder
        command = "cp -r %s %s" % (self.template, team_folder)
        code = os.system(command)
        if code != 0:
            print("Error while executing command: %s" % (command))
            return
        print("team folder created")
        print("configuring vaiables")
        self.config_team(team_id, config)
        print("create team envrionment finished")

    def config_team(self, team_id, config):
        print("Modifying team %d => \n%s" % (team_id, config))
        docker_compose_content = open("%s/docker-compose.yml" % (config['team_folder'])).read()
        docker_compose_content = docker_compose_content.replace(
            "__SERVICE_EXTERNAL_PORT___", str(config['service_port'])
        )
        docker_compose_content = docker_compose_content.replace(
            "__SSH_EXTERNAL_PORT___", str(config['ssh_port'])
        )
        docker_compose_content = docker_compose_content.replace(
            "__IP__", config['ip']
        )
        docker_compose_content = docker_compose_content.replace(
            "__SUBNET__", config['subnet']
        )
        docker_compose_content = docker_compose_content.replace(
            "__GATEWAY__", config['gateway']
        )
        print docker_compose_content
        

    def count_team(self):
        number =  len(os.listdir(self.playground))
        print("Current team number: %d" % (number))
        return number

        
    def help(self, func):
        try:
            print("%s: " % (func))
            print(getattr(self, func).__doc__)
        except AttributeError as e:
            print("%r" % e)
            print("No such command: %s" % (func))
        except TypeError as e:
            print("Type error: %s" % (repr(e)))


    def dispatcher(self, func, *args):
        try:
            getattr(self, func)(*args)
        except AttributeError as e:
            print("%r" % e)
            print("No such command: %s" % (func))
        except TypeError as e:
            print("Type error: %s" % (repr(e)))
        


def main():
    manager = Manager("../playground", "../challenge/template")
    manager.dispatcher(*sys.argv[1:])

if __name__ == "__main__":
    main()

