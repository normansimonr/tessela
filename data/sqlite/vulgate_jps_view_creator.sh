#!/bin/bash

DB="bible.db"

sqlite3 "$DB" <<'SQL'

DROP VIEW IF EXISTS vulgate_jps_master;

CREATE VIEW vulgate_jps_master AS

-- All Vulgate verses, with JPS if present
SELECT
    b.verseID                             AS verseID,
    b.book                                AS book,
    b.chapter                             AS chapter,
    b.startVerse                          AS startVerse,
    b.endVerse                            AS endVerse,
    b.verseText                           AS vulgate_text,
    j.verseText                           AS jps_text,
    CASE WHEN j.verseID IS NULL THEN 1 ELSE 0 END AS missing_in_jps,
    0 AS missing_in_vulgate
FROM engDRA_vpl b
LEFT JOIN engjps_vpl j ON b.verseID = j.verseID

UNION ALL

-- Verses only in JPS
SELECT
    j.verseID,
    j.book,
    j.chapter,
    j.startVerse,
    j.endVerse,
    NULL            AS vulgate_text,
    j.verseText     AS jps_text,
    0               AS missing_in_jps,
    1               AS missing_in_vulgate
FROM engjps_vpl j
LEFT JOIN engDRA_vpl b ON j.verseID = b.verseID
WHERE b.verseID IS NULL;

SQL
 
