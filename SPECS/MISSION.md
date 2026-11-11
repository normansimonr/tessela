# TESSELA --- Mission

## 1. Mission

TESSELA is a research and decision-support system for the textual
criticism of the Hebrew Bible, built to help a translator evaluate a
large and complex body of textual evidence efficiently, transparently,
and consistently.

Its purpose is to automate a substantial part of the work involved in
identifying, organizing, comparing, and evaluating textually significant
variants---while keeping scholarly judgment, uncertainty, and
traceability at the centre of the process.

TESSELA will bring together readings from the Masoretic tradition and
other ancient witnesses, relevant scholarly discussions, explicit
hypotheses about the development of the text, and structured AI-assisted
analysis. It will help the researcher understand what the evidence may
indicate, why competing explanations are plausible, and how strongly
each conclusion is supported.

TESSELA is a research assistant, not an autonomous textual critic. It
must not conceal uncertainty, manufacture evidence, or present an
AI-generated reconstruction as an attested reading.

## 2. The problem

The textual criticism of the Old Testament involves a very large number
of textual variants distributed across manuscripts, ancient
translations, scholarly editions, and secondary literature. Evaluating
these variants individually can require an enormous amount of
time---potentially months or years.

For a translator, not every difference is equally important. Many
variants are orthographic, morphological, or otherwise have little or no
effect on the meaning of a passage. The primary concern of TESSELA is
therefore to identify and evaluate variants that may materially affect
interpretation or translation.

The project aims to reduce the manual workload by:

-   consolidating relevant readings and evidence in a structured
    dataset;
-   aligning witnesses and identifying potentially significant
    differences;
-   distinguishing meaningful variants from differences that do not
    materially affect meaning;
-   locating and incorporating relevant scholarly discussion;
-   generating explicit, competing hypotheses about how readings may
    have developed;
-   evaluating those hypotheses against textual, linguistic, contextual,
    and other relevant evidence; and
-   producing reasoned, traceable assessments that support the
    translator's decisions.

Automation should make the work more manageable, not make the reasoning
less rigorous.

## 3. Scope and textual witnesses

TESSELA will initially focus on the following witnesses and sources.

### 3.1 The Masoretic Text

The Masoretic Text (MT) is the principal base text against which other
readings are compared.

The available data includes the MT, together with its Qere and Ketiv
readings. For both forms, the dataset includes morphological parsing and
lexical root information.

Qere and Ketiv differences should be represented explicitly rather than
flattened into a single reading. For example, a Ketiv reading meaning
"he called" and a Qere reading meaning "I called" differ in person and
therefore potentially affect the meaning of the passage.

### 3.2 Samaritan Pentateuch

TESSELA will include a curated set of readings from the Samaritan
Pentateuch (SP). The initial collection contains approximately twenty
selected variants.

At present, this collection identifies the relevant verses and variants
in English, but does not include the corresponding Hebrew text. The
system should preserve this distinction in the data: an English
description of a variant is not equivalent to a directly transcribed
Hebrew reading.

Where possible, the project may later enrich these records with the
underlying Hebrew readings and precise source references.

### 3.3 Dead Sea Scrolls

TESSELA will include a curated collection of approximately 150 variants
from the Dead Sea Scrolls (DSS).

As with the Samaritan Pentateuch collection, the current data identifies
relevant verses and variants in English but does not yet contain the
underlying Hebrew text for every reading.

The system must record the nature and limitations of the available
evidence. It should not imply that a Hebrew reading has been directly
inspected or transcribed when the dataset currently contains only an
English description.

### 3.4 Septuagint

The Septuagint (LXX) is a major source of evidence for the history of
the Hebrew text. Because it is a Greek translation, its readings cannot
simply be treated as Hebrew manuscript readings.

TESSELA will use Immanuel Tov's proposed Hebrew retroversions where he
argues that the Greek reflects a Vorlage that differed from the
Masoretic Text. Such retroversions will be treated as **reconstructed
Hebrew readings**, not as directly attested Hebrew manuscript evidence.

This distinction is fundamental. The Greek wording is the attested
evidence; a proposed Hebrew Vorlage is an interpretation of that
evidence. The system must retain the chain of reasoning and attribution
connecting the Greek reading to the proposed Hebrew retroversion,
including uncertainty and alternative explanations where available.

The project has also experimented with comparing Robert Brenton's
English translation of the Septuagint with the Jewish Publication
Society's English translation of the Masoretic Text. An AI pipeline
compared the translations verse by verse and flagged differences in
meaning.

This approach was not sufficiently reliable, in part because the
Septuagint and Masoretic Text do not always share the same
versification. Any future alignment and comparison pipeline must account
for differences in versification, textual division, and translation
choices. English translations may be useful as an initial discovery aid,
but they should not be treated as a substitute for examining the
underlying Greek and Hebrew evidence.

### 3.5 Vulgate

TESSELA should incorporate the Latin Vulgate as an additional witness,
primarily for completeness and corroboration.

Where a Vulgate reading appears to reflect a Hebrew Vorlage different
from the Masoretic Text, the project may investigate a possible Hebrew
retroversion. Such a retroversion must be labelled as a reconstruction
and must not be confused with a directly attested Hebrew reading.

The Latin evidence, any proposed retroversion, the reasoning behind it,
and the degree of confidence should be stored separately.

### 3.6 Peshitta

TESSELA should also incorporate the Syriac Peshitta as an additional
witness.

As with the Vulgate, the Peshitta may preserve evidence relevant to the
history of the Hebrew text. Where appropriate, the system may
investigate possible Hebrew retroversions, while clearly distinguishing
the attested Syriac reading from any reconstructed Hebrew Vorlage.

### 3.7 Scholarly literature: Dominique Barthélemy's *Critique Textuelle de l'Ancien Testament*

The project has PDFs of Dominique Barthélemy's *Critique Textuelle de
l'Ancien Testament* (CTAT), together with an index mapping variants of
interest to the pages on which they are discussed.

TESSELA should use this mapping to retrieve the relevant discussion when
evaluating a variant. The PDFs provide an important source of scholarly
analysis and should be treated as evidence to be consulted and cited,
not as an opaque authority whose conclusions are accepted automatically.

The system should preserve bibliographic details and page-level
references so that claims derived from the work can be checked against
the original discussion.

### 3.8 Further scholarly literature

Where relevant, TESSELA should identify and retrieve open-access
scholarly papers, articles, and other research dealing with particular
textual variants.

Retrieved literature should be linked to the specific variant or
question it addresses. The system should extract relevant arguments and
evidence with precise citations, distinguish an author's claims from the
system's own analysis, and avoid treating the mere existence of a
publication as proof that its conclusions are correct.

Copyright, licensing, and access restrictions must be respected when
collecting and storing scholarly material.

## 4. What counts as a significant variant?

TESSELA is primarily concerned with variants that may affect the meaning
of a passage and, consequently, its interpretation or translation.

Not every difference between witnesses should be treated as equally
significant. Differences that are merely orthographic, stylistic, or
morphological---and that do not materially change the meaning---are
generally outside the project's main analytical priority.

For example:

-   A difference between readings corresponding to "he called" and "I
    called" may be significant because it changes the grammatical person
    and potentially the meaning.
-   A difference in verbal form that does not materially change the
    sense in context may be less important for the project's purposes.
-   A difference between a Hebrew divine designation represented by
    "Adonai" and a Greek rendering represented by *theos* ("God") may
    not warrant priority if the difference does not materially affect
    the interpretation or translation under consideration.

These examples are illustrative, not universal rules. Significance must
be assessed in context. A seemingly small grammatical or lexical
difference can matter in a particular passage, while a visibly different
form may have little interpretive consequence.

The system should therefore distinguish at least:

1.  **Formal difference:** the witnesses differ in wording, spelling,
    morphology, or another textual feature.
2.  **Semantic difference:** the readings may communicate different
    meanings.
3.  **Interpretive or translational significance:** the difference may
    affect how the passage should be understood or translated.

TESSELA should retain potentially relevant formal differences even when
they are judged not to affect meaning. This makes the filtering process
auditable and allows a researcher to revisit decisions.

## 5. Core capabilities

### 5.1 A structured, source-aware variant dataset

TESSELA should build and maintain a structured dataset of textual
variants. Each record should make it possible to determine:

-   the biblical book, chapter, verse, and relevant textual location;
-   the base-text reading in the Masoretic Text;
-   the Qere and Ketiv readings, where applicable;
-   the readings or descriptions supplied by other witnesses;
-   whether a reading is directly attested, reconstructed, or known only
    through a secondary description;
-   the language and textual tradition of each witness;
-   morphological parsing and lexical roots, where available;
-   the source from which the reading or claim was obtained;
-   the relevant scholarly discussion and page references;
-   alignment information and any uncertainty about that alignment; and
-   the system's assessment of whether the difference may affect
    meaning.

The dataset must preserve provenance. It should always be possible to
trace a reading, reconstruction, or scholarly claim back to its source.

Missing information must remain explicitly missing. The system must not
silently fill gaps by guessing.

### 5.2 Witness alignment and variant discovery

TESSELA should align readings across the relevant witnesses and identify
possible differences.

This is especially important when comparing texts with different
versification systems or textual divisions. Alignment should not rely
solely on matching chapter and verse numbers. It should be able to
represent cases where one witness divides, combines, omits, or reorders
material differently.

Automated comparison of English translations may be used to discover
candidate differences, but it should be treated as a preliminary method.
Where possible, comparisons should be performed on the original
languages and checked against reliable editions and scholarly sources.

The system should distinguish:

-   a confirmed textual difference;
-   a possible difference requiring verification;
-   a difference caused by translation choices;
-   a difference caused by versification or alignment; and
-   a difference whose textual significance is uncertain.

### 5.3 Semantic evaluation

For each candidate variant, TESSELA should assess whether the competing
readings differ in meaning and whether that difference matters for
translation.

This evaluation should consider, as appropriate:

-   lexical meaning;
-   morphology and syntax;
-   grammatical person, number, gender, tense, aspect, and verbal stem;
-   clause structure and relationships between words;
-   immediate literary context;
-   broader literary and canonical context;
-   idiom and usage elsewhere in the Hebrew Bible;
-   translation technique in ancient versions; and
-   interpretive or theological implications.

The system should explain why a difference is or is not considered
meaningful. It should not reduce semantic evaluation to a binary label
without preserving the reasoning.

### 5.4 Scholarly source retrieval

For each variant, TESSELA should retrieve relevant material from the
CTAT PDFs and other available scholarly literature.

The system should identify the specific arguments made by scholars, the
evidence they cite, and the conclusions they reach. It should preserve
exact bibliographic and page references and distinguish direct
quotations, paraphrases, and the system's own conclusions.

When sources disagree, the disagreement should be represented rather
than prematurely resolved.

## 6. Reconstructing the development of the text

A central ambition of TESSELA is to move beyond listing variant readings
and explore plausible hypotheses about how the textual tradition
developed.

For a given passage, the system should take the available readings from
the Masoretic Text, Qere and Ketiv, Samaritan Pentateuch, Dead Sea
Scrolls, Septuagint, Vulgate, Peshitta, and relevant scholarly
reconstructions, and explore possible relationships among them.

The aim is to construct explicit models of textual development. These
models may be represented as directed graphs or trees in which:

-   nodes represent readings or textual states;
-   edges represent proposed changes from one reading to another;
-   each edge is associated with a proposed scribal, linguistic,
    translational, or other mechanism;
-    each edge is assigned a probability of being true;
-   each node and edge is linked to the evidence that supports or
    challenges it; and
-   alternative models represent competing explanations of the same
    evidence.

For example, suppose the Masoretic Text has a Hebrew reading *Adonai*,
while the Septuagint has the Greek *theos*. One hypothesis might begin
with the Masoretic reading and propose that a different Hebrew
expression, such as *Elohim*, arose at an earlier or later stage and was
reflected in the Greek translation. Another hypothesis might instead
treat the reading underlying the Septuagint as earlier and propose that
the Masoretic reading developed from it.

These are examples of the kinds of hypotheses the system should be able
to represent, not conclusions to be assumed in advance. The actual
direction and plausibility of a proposed development must be evaluated
against the linguistic, textual, historical, and contextual evidence.

### 6.1 Systematic exploration of competing hypotheses

TESSELA should explore materially distinct hypotheses rather than
considering only the most obvious explanation.

For example, it should be possible to compare:

-   a hypothesis in which the Masoretic reading is original and other
    readings developed from it;
-   a hypothesis in which a non-Masoretic reading is earlier and the
    Masoretic reading is secondary; and
-   hypotheses in which multiple readings descend from an earlier form
    that is not preserved directly by any surviving witness.

The system should generate candidate models systematically, using
deterministic procedures combinatorially where possible and AI-assisted reasoning where
useful.

### 6.2 Scribal and translational tendencies

The evaluation of hypotheses should account for known or proposed
scribal tendencies and mechanisms of textual change.

These may include, where relevant:

-   visual confusion between similar Hebrew letters, such as *waw* and
    *yod*;
-   omissions, additions, and repetitions;
-   harmonization to parallel passages or familiar expressions;
-   grammatical or lexical normalization;
-   changes motivated by clarification or simplification;
-   deliberate or inadvertent changes in wording;
-   changes arising during translation; and
-   retroversion uncertainties introduced when reconstructing a Hebrew
    Vorlage from an ancient translation.

Such tendencies should be encoded as explicit analytical considerations,
not treated as universal laws. For instance, the visual similarity of
*waw* and *yod* may make a proposed change plausible, but it does not by
itself establish the direction of change or prove that the change
occurred.

The system should evaluate each proposed transition in its textual and
historical context and record both supporting and opposing
considerations.

### 6.3 Evidence and uncertainty

Every hypothesis should be accompanied by an explanation of the evidence
for and against it.

Relevant considerations may include:

-   the age, character, and textual affiliation of witnesses;
-   the distribution of readings across witnesses;
-   the relationship and possible dependence between witnesses;
-   Hebrew grammar, syntax, and lexicon;
-   scribal and translational tendencies;
-   the immediate and broader context;
-   the explanatory power and relative simplicity of the proposed
    development; and
-   the views and arguments found in relevant scholarship.

TESSELA may assign comparative scores or probabilities to hypotheses,
but these must not create a false impression of mathematical certainty.
Scores should be based on explicit criteria, assumptions, and evidence.
Where probabilities are used, the system should explain what they
represent, how they were derived, and what limitations apply.

In particular, witnesses must not automatically be counted as
independent votes. Their relationships, shared ancestry, translation
dependencies, and other forms of textual dependence can affect the
evidential weight of their readings.

The system should preserve uncertainty at the level of individual
readings, alignments, proposed transitions, and complete hypotheses.

## 7. AI-assisted textual criticism

TESSELA will use AI to assist with evidence synthesis, hypothesis
generation, argument construction, and evaluation. AI should make the
research process faster and more systematic while remaining accountable
to the underlying evidence.

A proposed multi-agent workflow consists of three principal agents.

### 7.1 Mónica --- the Masoretic Text advocate

Mónica is tasked with constructing the strongest evidence-based case in
favour of the Masoretic Text reading.

She should examine the available textual evidence, linguistic
considerations, literary context, relevant scholarly literature, and
interpretive or theological considerations where relevant.

Her role is not to defend the Masoretic Text regardless of the evidence.
She should present the strongest defensible case for it.

### 7.2 Tomás --- the challenger of the Masoretic Text

Tomás is tasked with constructing the strongest evidence-based case
against the Masoretic Text reading when competing readings are
available.

He should examine the same body of evidence and consider whether
non-Masoretic readings, or a reconstructed earlier reading, provide a
better explanation of the textual data.

His role is to reject the Masoretic Text automatically and provide
the best possible rationale for that position, based on the evidence.

### 7.3 Ernesto --- the adjudicator

Ernesto receives the evidence, Monica's argument, and Tomás's argument.
He evaluates the competing cases and produces a reasoned assessment.

Ernesto should:

-   assess whether both agents have represented the evidence accurately;
-   identify unsupported claims, omissions, and questionable
    assumptions;
-   compare the explanatory strength of the competing hypotheses;
-   consider the quality, relevance, and independence of the witnesses;
-   assess linguistic, contextual, scribal, translational, theological and scholarly
    arguments;
-   distinguish established facts from inferences and conjectures;
-   explain what evidence would be needed to resolve remaining
    uncertainties; and
-   provide a calibrated conclusion rather than forcing a verdict when
    the evidence is inconclusive.

The agents should have access to the same underlying evidence and source
material. Their different roles should encourage critical examination,
not create artificial disagreement or permit either advocate to ignore
inconvenient evidence.

### 7.4 Agent accountability

All agents must ground factual claims in the dataset or retrievable
sources. They should cite the specific readings, source passages, and
scholarly references on which their arguments depend.

They must not invent manuscript readings, bibliographic references,
scholarly positions, or historical explanations. When evidence is
unavailable, they must say so.

AI-generated claims should be distinguishable from claims directly
supported by a source. The system should retain the arguments and
evidence used in an assessment so that a researcher can inspect,
challenge, and revise the result.

## 8. Principles and methodological safeguards

The following principles should govern the design and operation of
TESSELA.

### 8.1 Evidence before conclusions

The system must begin with the available evidence and make its reasoning
explicit. It must not select a preferred reading first and then assemble
a case to justify it.

### 8.2 Preserve the distinction between witnesses and reconstructions

A reading directly attested in a Hebrew manuscript is not the same kind
of evidence as a Hebrew retroversion proposed on the basis of a Greek,
Latin, or Syriac translation. The system must preserve these
distinctions throughout storage, analysis, visualization, and reporting.

### 8.3 Preserve provenance and traceability

Every reading, claim, alignment, reconstruction, and scholarly argument
should be traceable to its source. Conclusions should link back to the
evidence on which they depend.

### 8.4 Make uncertainty explicit

TESSELA must not turn missing data, ambiguous alignments, uncertain
retroversions, or disputed interpretations into apparently certain
facts. Uncertainty should be recorded and communicated at the
appropriate level.

### 8.5 Treat witnesses critically

The number of witnesses supporting a reading is not, by itself, a
sufficient measure of its strength. The date, textual character,
relationships, and possible dependencies of witnesses must be
considered.

### 8.6 Distinguish textual evidence from interpretation

The system should distinguish what a witness actually says from what a
scholar infers about its Vorlage, what an AI agent proposes about
textual development, and what a translator decides to do with the
resulting evidence.

### 8.7 Avoid predetermined outcomes

The Masoretic Text should neither be privileged as correct by default
nor rejected because another reading appears preferable. Monica and
Tomás should operate as disciplined advocates, while Ernesto should
evaluate their arguments impartially.

### 8.8 Be reproducible and inspectable

Where possible, data transformations, alignment decisions, filtering
rules, hypothesis-generation procedures, and scoring methods should be
deterministic and documented. AI-assisted steps should record the
inputs, outputs, model or method used, and relevant instructions or
configuration.

### 8.9 Keep the translator in control

TESSELA supports scholarly judgment and translation decisions; it does
not make those decisions on the translator's behalf. Its output should
help the researcher understand the evidence and its implications, not
replace the researcher's responsibility.

## 9. Intended workflow

The overall workflow is envisaged as follows:

1.  **Collect and register sources.** Import the Masoretic Text and its
    Qere/Ketiv data, curated Samaritan Pentateuch and Dead Sea Scrolls
    variants, Tov's Septuagint retroversions, and relevant scholarly
    resources.
2.  **Normalize and structure the data.** Represent readings, witnesses,
    references, morphology, roots, provenance, and uncertainty in a
    consistent format.
3.  **Align witnesses.** Associate readings with the appropriate textual
    locations while accounting for differences in versification and
    textual division.
4.  **Discover candidate variants.** Identify differences between
    witnesses and record how each candidate was detected.
5.  **Evaluate semantic significance.** Assess whether each difference
    may affect meaning or translation, preserving the reasoning and
    uncertainty.
6.  **Retrieve scholarly discussion.** Locate the relevant CTAT pages
    and other research, extracting arguments with precise references.
7.  **Generate textual-development hypotheses.** Construct plausible
    models of how the readings may be related and how changes may have
    occurred.
8.  **Evaluate hypotheses.** Apply explicit linguistic, textual,
    contextual, scribal, translational, and scholarly criteria.
9.  **Conduct adversarial AI analysis.** Have Monica and Tomás construct
    competing cases, then have Ernesto assess them against the evidence.
10. **Present a research report.** Provide the readings, sources,
    alignments, hypotheses, arguments, uncertainty, and a reasoned
    assessment for the translator to review.

This workflow is iterative. A researcher should be able to correct a
reading or alignment, add a source, challenge an assumption, or
introduce a new hypothesis and then rerun the relevant analyses.

## 10. Expected outputs

For each significant variant, TESSELA should ultimately be able to
produce a research dossier containing:

-   the relevant textual location;
-   the Masoretic Text, Qere, and Ketiv readings, as applicable;
-   the readings or descriptions available from each other witness;
-   a clear indication of which readings are directly attested and which
    are reconstructed;
-   the original-language evidence available and any missing data;
-   alignment notes and uncertainty;
-   a semantic assessment of the differences;
-   relevant CTAT discussion and other scholarly sources;
-   competing textual-development hypotheses, preferably represented
    graphically;
-   the proposed changes connecting readings and the rationale for each;
-   evidence supporting and challenging each hypothesis;
-   the arguments produced by Monica and Tomás;
-   Ernesto's assessment and its supporting reasons; and
-   an overall statement of confidence, limitations, and unresolved
    questions.

The output should be useful for scholarly review and practical
translation work. It should make clear not only what TESSELA concludes,
but why it reaches that conclusion and what could change it.

## 11. Long-term direction

The initial priority is to build a reliable, source-aware dataset and
analytical workflow around the material already available: the Masoretic
Text and Qere/Ketiv data, selected Samaritan Pentateuch and Dead Sea
Scrolls variants, Tov's Septuagint retroversions, and Barthélemy's CTAT
discussions.

The Vulgate, Peshitta, additional scholarly literature, improved
original-language alignment, and more advanced hypothesis modelling can
be incorporated progressively.

The long-term ambition is for TESSELA to provide a comprehensive
environment in which a translator can investigate textually significant
variants, explore competing explanations of the history of the text, and
make informed decisions without having to reconstruct the entire
evidential landscape manually for every passage.

TESSELA should combine the efficiency of automation with the caution,
transparency, and critical discipline required by serious textual
scholarship.
