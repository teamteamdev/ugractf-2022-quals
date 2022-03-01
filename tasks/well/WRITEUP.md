# Well known and loved: Write-up

В таске было несколько отсылок на то, что ответ может быть как-то связан с `.well-known` — [специальный путь](https://www.rfc-editor.org/rfc/rfc8615) для различных сервисов, которые хотят отдавать какую-то метаинформацию — например, специальные ссылки для [iOS](https://developer.apple.com/library/archive/documentation/General/Conceptual/AppSearch/UniversalLinks.html) или [Android](https://developers.google.com/digital-asset-links/v1/getting-started), или коды подтверждений для автоматического получения [TLS-сертификатов](https://en.wikipedia.org/wiki/Automatic_Certificate_Management_Environment).

Список всего, что может находиться в этой директории по стандарту, можно найти [на сайте IANA](https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml). Осталось просто перебрать все эти файлы.

По адресу `https://well.q.2022.ugractf.ru/.well-known/matrix` вместо ожидаемой ошибки 404 мы получаем 403 — доступ запрещён. В той же таблице находим стандарт Matrix, в котором говорится о существовании двух файлов — `matrix/server` и `matrix/client`. И, действительно, из этих файлов мы узнаём о существовании сервера для мессенджера Matrix на порту 5000.

Подключимся к нему любым клиентом — например, [Element](https://app.element.io). Смотрим каналы — видим публичный, но закрытый, канал `kittens`, а в нём — флаг от одного из организаторов.

Флаг: **ugra_matrix_is_well_known_to_everyone_31b66f2022d2e62ed**
