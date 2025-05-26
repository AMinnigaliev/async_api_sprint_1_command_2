#!/bin/bash

set -e

echo "Добавление шардов через mongos1..."
mongosh --host "mongos1" --eval '
  sh.addShard("mongors1/mongors1n1:27017");
  sh.addShard("mongors2/mongors2n1:27017");
'
echo "→ OK"

echo "Создание базы '$MONGO_NAME'..."
mongosh --host "mongors1n1" --eval "
  use $MONGO_NAME;
"

echo "Включение шардирования для базы '$MONGO_NAME'..."
mongosh --host "mongos1" --eval "
  sh.enableSharding(\"$MONGO_NAME\");
"
echo "→ OK"

echo "Шардирование коллекций..."
declare -A shards=(
  [film_ratings]=user_id
  [film_reviews]=film_id
  [review_ratings]=review_id
  [bookmarks]=user_id
  [overall_film_ratings]=film_id
  [overall_review_ratings]=review_id
)
for coll in "${!shards[@]}"; do
  key=${shards[$coll]}
  echo -n "  $coll -> $key... "
  mongosh --host "mongos1" --eval "
    sh.shardCollection(\"$MONGO_NAME.$coll\", { $key: 'hashed' });
  "
  echo "OK"
done

echo "Все шаги выполнены успешно."
