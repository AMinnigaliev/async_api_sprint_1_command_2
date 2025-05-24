#!/bin/bash

set -e

echo "Настройка серверов конфигурации..."

mongosh '
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

