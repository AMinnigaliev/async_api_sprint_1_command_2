## Логика работы с событиями.
1. **Flask** принимает JSON:

    - Отслеживание кликов.

          {
             "event": "element_click",
             "token": "srt | null",
             "data": {
                 "element_type": "str" (movie, category, trailer и т.д.),
                 "page_type": "str" (movie, category, promotion и т.д.),
             }
          }

    - Отслеживание просмотров страниц.
    
      Для отслеживания времени проводимого пользователем на страницах, клиент должен генерировать ***"page_view_id"*** и 
      сохранять до момента ухода с просматриваемой страницы, для того что-бы можно было явно отслеживать связанные 
      сообщения о событиях данного типа.

          {
             "event": "str" (page_view_start или page_view_end),
             "token": "srt | null",
             "data": {
                 "page_view_id": "UUID",
                 "page_type": "str" (movie, category, promotion и т.д.),
             }
          }

   - Смена качества видео.
   
         {
             "event": "quality_change",
             "token": "srt | null",
             "data": {
                 "video_id": "str",
                 "old_quality": "int",
                 "new_quality": "int",
             }
         }

   - Просмотр видео до конца.
   
         {
             "event": "video_complete",
             "token": "srt | null",
             "data": {
                 "video_id": "str",
                 "duration_total": "bool",
             }
         }

   - Использование фильтров поиска.
   
         {
             "event": "search_filter",
             "token": "srt | null",
             "data": {
                 "search_query": "str",
                 "filters": "str",
             }
         }

2. Для ненулевого значения ***"token"*** производится проверка токена через **auth_service** с учётом кеша в Redis.
В случаи недоступности сервиса **auth_service** производится локальная проверка токена без учёта его времени жизни.
По результатам проверки, данные обогащаются ключом ***"user_id"*** с ID пользователя или значением *"anonymous"* если 
токен отсутствовал. А ***"token"*** удаляется из сообщения.

3. Данные обогащаются временной меткой ***"timestamp"*** и публикуются в единый топик **Kafka** с ключом, взятым из 
***"event"***.

4. ETL-сервис (по расписанию) читает новые сообщения из **Kafka**.

5. Все сформированные и валидные сообщения **ETL** отправляет в соответствующую значению ***"event"*** таблицу 
**ClickHouse**.