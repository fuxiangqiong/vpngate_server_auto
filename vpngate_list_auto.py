from urllib.request import Request,urlopen
import re
import base64
import socket
import os,glob
import csv

# vpn_list = 'http://enigmatic-scrubland-4484.herokuapp.com/'

# # get serer list from list url
# ua = Request(vpn_list)
# ua.add_header('User-agent', 'Mozilla/5.0')

# res = urlopen(ua)

def tcp_port_is_open(ip, port) :
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    r = s.connect_ex((ip, port))
    if r == 0 :
        s.close()
        return True
    else :
        return False

filename = 'server_list.txt'
result = {}
with open(filename, 'r',encoding='utf-8') as file:
    reader = csv.reader(file)
    # # 跳过前两行注释
    # next(reader)  # 跳过第一行
    # next(reader)  # 跳过第二行
    for row in reader:
        #row行上以*或者#开头的行都是注释，跳过
        if row[0].startswith('*') or row[0].startswith('#'):
            continue
        ip = row[1]
        port = int(row[2])
        country = row[6]
        config_base64 = row[-1]
        config = base64.b64decode(config_base64)
        print (ip+":"+country)

        # 将 config 转换为字节字符串
        config = config.decode('utf-8') 

        # get tcp port from config_file
        p_tcp = re.compile(r'^proto tcp', re.MULTILINE)
        p_port = re.compile(r'^remote [.|\d]+ (\d+)', re.MULTILINE)
        if p_tcp.search(config) :
            m_port = p_port.search(config)
            if m_port :
                port = int(m_port.group(1)) # 80 is num, '80' is str, it's different betwen perl and python
    #                        print ip, port
                if tcp_port_is_open(ip, port) :
                    print("GOOD: " + ip + ":" + str(port))
                    if not country in result :
                        result[country] = []
                    else :
                        result[country].append({'ip':ip, 'config':config})
                else :
                    print ("TIMEOUT: " + ip + ":" +str(port))
    
    #print result
    
    # rm old file
    config_path = 'config'
    os.chdir(os.path.join(os.getcwd(), config_path))
    for conf in glob.glob('vpngate*.ovpn') :
        os.remove(conf)

    # write to file, every country limit 50 server
    for country in result :
        for server in result[country][0:50] :
#            print server
            file_name = '_'.join(['vpngate', country, server['ip']]) + '.ovpn'
            print(file_name)
            f = open(file_name, 'w')
            f.write(server['config'])
            f.close()