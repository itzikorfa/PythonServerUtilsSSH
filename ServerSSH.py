
import subprocess
import platform
import logging
import sys
import socket
import paramiko
import argparse

class Server(object):
    def __init__(self,server,port,user,password):
        self.server=server
        self.port=port
        self.user=user
        self.password=password
        if not self.validateInput():
            raise Exception("input validation error")

        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='[%(asctime)s] %(message)s',
                            datefmt='%d/%m/%Y | %H:%M:%S')
    def __str__(self):
        return "{}:{}".format(self.server, self.port)

    def validateInput(self):
        try:
            socket.gethostbyname(self.server)
            num=int(self.port)
            if (num<10 or num>100000):
                raise Exception("port out of range")
            if (self.user == None or len(self.user)==0 \
                        or self.password == None or len(self.password)==0):
                raise Exception("invalid user name or password")
            return True
        except socket.error:
            logging.info("server input error")
            return False
        except ValueError:
            logging.info("port input error")
            return False
        except Exception as exp:
            logging.info(exp)
            return False

    def isAlive(self):
        ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 1"
        args = "ping " + " " + ping_str + " " + self.server
        need_sh = False if  platform.system().lower()=="windows" else True
        res = subprocess.call(args,need_sh);
        logging.info("ping to machine {} resualt {}".format(self.server,res))
        return res

    def getStdInfo(self, stream):
        res=""
        for line in stream.read().splitlines():
            res+=str(line,encoding='utf8')
            res+='\n'
        return res

    def sendFileViaSSH(self,file=""):
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.server, 22, self.user, self.password)

            transport = ssh.get_transport()
            with transport.open_channel(kind='session') as channel:
                file_data = open(file, 'rb').read()
                channel.exec_command('cat > remote_file')
                channel.sendall(file_data)
        ssh.close()



    def runCmdViaSSH(self,cmd="",getoutput=True):
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.server, 22, self.user, self.password)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            err=self.getStdInfo(stderr)
            if len(err)>0:
                logging.error("command{},  error: {}".format(cmd, err))
            # get results output
            output=self.getStdInfo(stdout)
            logging.info("output: {}".format(output))
            ssh.close()
            return None if not getoutput else output

    def isStrInCmdOutput(self,cmd,output):
        res=str(self.runCmdViaSSH(cmd,True))
        try:
            res.index(output)
            return True
        except ValueError:
            return False



def parse_args(args):
    machine_ip = args.machine_ip[0] if args.machine_ip else None
    # test_type = args.test_type[0]
    # install_new_take = False if args.no_install == 'true' else True
    branch = args.branch[0] if args.branch else None
    take = args.take[0] if args.take else None
    user = args.user[0] if args.user else None
    password=args.password[0] if args.password else None
    port=args.port[0] if args.port else None

    return machine_ip, port,branch, take,user,password


def main():
    # args = args_initializer()
    # machine_ip, port, branch, take, user,password = parse_args(args)
    ser = "192.168.153.131"
    # port="220"
    ser=Server(server=ser,port=220,user="izia", password="lkjmnb")
    print(ser.isAlive())
    ser.sendFileViaSSH("test.txt")
    print(ser.runCmdViaSSH("ls"))
    print(ser.isStrInCmdOutput("ls", "st"))




if __name__ == '__main__':
    main()