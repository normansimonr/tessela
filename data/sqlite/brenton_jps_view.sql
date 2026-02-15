DROP VIEW IF EXISTS brenton_jps_master;

CREATE VIEW brenton_jps_master AS

-- All Brenton verses, with JPS if present
SELECT
    b.verseID                             AS verseID,
    b.book                                AS book,
    b.chapter                             AS chapter,
    b.startVerse                          AS startVerse,
    b.endVerse                            AS endVerse,
    b.verseText                           AS brenton_text,
    j.verseText                           AS jps_text,
    j.hebrew_chapter                      AS hebrew_chapter,
    j.hebrew_startVerse                   AS hebrew_startVerse,
    j.hebrew_endVerse                     AS hebrew_endVerse,
    CASE WHEN j.verseID IS NULL THEN 1 ELSE 0 END AS missing_in_jps,
    0 AS missing_in_brenton
FROM eng_Brenton_vpl b
LEFT JOIN engjps_vpl_with_hebrew j
       ON b.verseID = j.verseID

UNION ALL

-- Verses only in JPS
SELECT
    j.verseID                             AS verseID,
    j.book                                AS book,
    j.chapter                             AS chapter,
    j.startVerse                          AS startVerse,
    j.endVerse                            AS endVerse,
    NULL                                  AS brenton_text,
    j.verseText                           AS jps_text,
    j.hebrew_chapter                      AS hebrew_chapter,
    j.hebrew_startVerse                   AS hebrew_startVerse,
    j.hebrew_endVerse                     AS hebrew_endVerse,
    0                                     AS missing_in_jps,
    1                                     AS missing_in_brenton
FROM engjps_vpl_with_hebrew j
LEFT JOIN eng_Brenton_vpl b
       ON j.verseID = b.verseID
WHERE b.verseID IS NULL;
