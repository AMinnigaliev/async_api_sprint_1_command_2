#!/bin/bash

set -e

echo "Настройка серверов конфигурации..."
mongosh --host "mongocfg1" --quiet --eval '
  rs.initiate({
    _id: "mongors1conf",
    configsvr: true,
    members: [
      { _id: 0, host: "mongocfg1:27017" },
      { _id: 1, host: "mongocfg2:27017" },
      { _id: 2, host: "mongocfg3:27017" }
    ]
  });
'
echo "→ OK"

echo "Сбор реплик первого шарда..."
mongosh --host "mongors1n1" --quiet --eval '
  rs.initiate({
    _id: "mongors1",
    members: [
      { _id: 0, host: "mongors1n1:27017" },
      { _id: 1, host: "mongors1n2:27017" },
      { _id: 2, host: "mongors1n3:27017" }
    ]
  });
'
echo "→ OK"

echo "Сбор реплик второго шарда..."
mongosh --host "mongors2n1" --quiet --eval '
  rs.initiate({
    _id: "mongors2",
    members: [
      { _id: 0, host: "mongors2n1:27017" },
      { _id: 1, host: "mongors2n2:27017" },
      { _id: 2, host: "mongors2n3:27017" }
    ]
  });
'
echo "→ OK"
