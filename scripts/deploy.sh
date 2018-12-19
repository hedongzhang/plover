#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/7

Author: 

Description: 

"""

INSTALL_PATH=/root/install

# 清理环境
rm $INSTALL_PATH
mkdir $INSTALL_PATH

# 安装基础包
yum install yum-utils screen zlib* pip -y

# 安装Python3
cd $INSTALL_PATH
wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
tar xzf Python-3.6.6.tgz
cd $INSTALL_PATH/Python-3.6.6
#python3兼容ssl需要解注释205行为: _socket socketmodule.c
sed -i "s/#_socket socketmodule.c/_socket socketmodule.c/g" Modules/Setup.dist
./configure && make && make install

# 手动安装mysql
cd $INSTALL_PATH
wget https://dev.mysql.com/get/mysql80-community-release-el7-1.noarch.rpm
rpm -ivh mysql80-community-release-el7-1.noarch.rpm
yum-config-manager --disable mysql80-community
yum-config-manager --enable mysql57-community
yum install mysql-community-server -y
mkdir /storage/database/data -p
chown mysql:mysql /storage/database/ -R
cp /root/plover/conf/my.cnf /etc/my.cnf
systemctl start mysqld
# grep 'temporary password' /storage/database/mysqld.log
# mysql -uroot -p
# ALTER USER 'root'@'localhost' IDENTIFIED BY 'Plover!Password1';
# create database polver

# 手动安装plover
cd $INSTALL_PATH
tar xzf plover.tgz
tar xzf ./plover/env/plover-env.tgz
mv ./plover /root/plover
mv ./plover-env /root/plover-env
echo "source /root/plover-env/bin/activate
export PYTHONPATH=/root/plover" >> /root/.bash_profile
source /root/.bash_profile

mkdir /storage/static
mkdir /storage/upload
mkdir /storage/upload/identify
mkdir /storage/upload/suggestion