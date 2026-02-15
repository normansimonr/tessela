create view engjps_vpl_with_hebrew as
select
    verseID,
    canon_order,
    book,
    chapter,
    startVerse,
    endVerse,
    verseText,

    case
        when verseText like '(%-%)%'
             and substr(verseText, 1, 1) = '('
        then cast(
                substr(
                    verseText,
                    2,
                    instr(verseText, '-') - 2
                ) as integer
             )
        else chapter
    end as hebrew_chapter,

    case
        when verseText like '(%-%)%'
             and substr(verseText, 1, 1) = '('
        then cast(
                substr(
                    verseText,
                    instr(verseText, '-') + 1,
                    instr(verseText, ')') - instr(verseText, '-') - 1
                ) as integer
             )
        else startVerse
    end as hebrew_startVerse,

    case
        when verseText like '(%-%)%'
             and substr(verseText, 1, 1) = '('
        then cast(
                substr(
                    verseText,
                    instr(verseText, '-') + 1,
                    instr(verseText, ')') - instr(verseText, '-') - 1
                ) as integer
             )
        else endVerse
    end as hebrew_endVerse

from engjps_vpl;

