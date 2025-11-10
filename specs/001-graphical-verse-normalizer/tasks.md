## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create `backend/` and `frontend/` directories in the repository root.
- [X] T002 Create `backend/requirements.txt` with FastAPI, Pandas, uvicorn, and google-generativeai.
- [X] T003 Update `frontend/requirements.txt` with Streamlit and requests.
- [X] T004 Create a unified `Dockerfile` at the project root for Cloud Run deployment.
- [X] T005 Create `run.sh` entrypoint script at the project root.
- [X] T006 [P] Configure initial `.gitignore` for backend and frontend.

---

## Phase 2: Foundational (Backend Normalization Service)

**Purpose**: Core infrastructure for the normalization service that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T007 Implement data loading logic for `data/masoretic.csv`, `data/vulgate.csv`, and `data/septuagint.csv` in `backend/src/data_loader.py`. This includes handling different book name representations (FR-008).
- [ ] T008 Implement the deep semantic decomposition logic in `backend/src/normalization_service.py`, including renaming the method to `decompose_text` and loading the prompt from `prompts/normalization_prompt.txt`.
- [X] T009 Create the FastAPI application instance in `backend/src/api/main.py`.
- [ ] T010 Implement the `/normalize` API endpoint in `backend/src/api/main.py` as defined in `contracts/openapi.json`. This endpoint should accept `NormalizationRequest` and return `NormalizationResponse`, calling the `decompose_text` method from `NormalizationService` and handling its `List[str]` output.
- [X] T011 Add unit tests for data loading logic in `backend/tests/test_data_loader.py`.
- [ ] T012 Add unit tests for deep semantic decomposition logic in `backend/tests/test_normalization_service.py`, ensuring coverage for JSON parsing and the expected output format.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Verse Normalization (Priority: P1) 🎯 MVP

**Goal**: Allow users to select a biblical verse and view its normalized text from three datasets in the graphical interface.

**Independent Test**: Select a verse from the dropdown and verify that the three text boxes are populated with the correct normalized text from Masoretic, Vulgate, and Septuagint datasets.

### Implementation for User Story 1

- [X] T013 [US1] Set up the Streamlit application in `frontend/src/app.py`.
- [X] T014 [US1] Implement the single dropdown menu for verse selection in `frontend/src/app.py`.
- [X] T015 [US1] Populate the dropdown with the union of all unique verses from the datasets (FR-001, FR-002). This will require an initial call to the backend to get the list of available verses.
- [X] T016 [US1] Implement the display of three distinct output text boxes in `frontend/src/app.py` (FR-005).
- [X] T017 [US1] Implement the logic to call the backend normalization service when a verse is selected in `frontend/src/app.py` (FR-003, FR-004).
- [X] T018 [US1] Handle cases where a verse is not found in a particular dataset, displaying a clear message (FR-007).
- [X] T019 [US1] Ensure each output area is clearly labeled with the dataset name (FR-006).

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: Deployment Unification

**Purpose**: Integrate backend and frontend into a single deployable unit for Cloud Run.

- [X] T020 Modify `frontend/src/app.py` to update `BACKEND_URL` to `http://localhost:8001` for internal communication.
- [X] T021 Remove `backend/Dockerfile`.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T022 Code cleanup and refactoring for both backend and frontend.
- [X] T023 Run `quickstart.md` validation.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Deployment Unification (Phase 4)**: Depends on Foundational and User Stories completion.
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
# (No specific test tasks generated for US1, as tests were not explicitly requested in spec)

# Launch all models for User Story 1 together:
# (No specific model tasks generated for US1, as data model is handled in backend)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. Complete Phase 4: Deployment Unification
5. **STOP and VALIDATE**: Test User Story 1 independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
