ES_HOME=/usr/share

sudo service elasticsearch stop

sudo mv ${ES_HOME}/elasticsearch ${ES_HOME}/elasticsearch_90

sudo mkdir ${ES_HOME}/elasticsearch

wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.7.2.tar.gz -O elasticsearch.tar.gz

tar -xf elasticsearch.tar.gz

sudo mv ./elasticsearch-1.7.2/ ./elasticsearch

sudo mv ./elasticsearch ${ES_HOME}/

sudo mv /var/lib/elasticsearch /var/lib/elasticsearch_90

sudo mkdir /var/lib/elasticsearch

sudo service elasticsearch start

sudo rm ./elasticsearch.tar.gz