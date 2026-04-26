DROP VIEW IF EXISTS brenton_jps_tov_master;

CREATE VIEW brenton_jps_tov_master AS

SELECT
    m.verseID,
    m.book,
    m.chapter,
    m.startVerse,
    m.endVerse,
    m.brenton_text,
    m.jps_text,
    m.hebrew_chapter,
    m.hebrew_startVerse,
    m.hebrew_endVerse,
    m.missing_in_jps,
    m.missing_in_brenton,
    t.potential_difference_verse
FROM brenton_jps_master m
LEFT JOIN tov_distilled t
       ON m.book = t.book
      AND m.hebrew_chapter = t.chapter
      AND m.hebrew_startVerse = CAST(t.verse AS INTEGER);
