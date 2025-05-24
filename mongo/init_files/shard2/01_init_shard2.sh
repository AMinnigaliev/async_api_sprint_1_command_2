#!/bin/bash

set -e

echo "Сбор реплик второго шарда..."

mongosh '
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
