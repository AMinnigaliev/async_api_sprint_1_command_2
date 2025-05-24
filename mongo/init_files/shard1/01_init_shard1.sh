#!/bin/bash

set -e

echo "Сбор реплик первого шарда..."

mongosh '
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
