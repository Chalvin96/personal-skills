# Contract & State positive control

This is a validation fixture, not normal review guidance. Do not load it during
an application-code review.

## Validation procedure

When changing contract-and-state.md, give this fixture and that reference to a
fresh reviewer. The reviewer must identify the partial-state warning below and
require a targeted failure test. A validation run is complete when the warning
is present, grounded in the commit ordering, and no unrelated style finding is
reported.

~~~python
class LessonImportService:
    async def activate_lesson_import(self, batch: LessonImportBatch) -> LessonRelease:
        revision = LessonRelease(is_active=True, digest=batch.digest)
        self.db.add(revision)
        await self.db.flush()
        await self.db.commit()

        await self._sync_practice_groups(batch)
        return revision
~~~

Expected warning:

The method commits the active release before it synchronizes the related
practice groups. If synchronization fails, the caller receives an import
failure while the release remains active without its required review
projections. Keep the activation and synchronization in one transaction with
one commit, or define and test an explicit recovery path.

A matching failure test must force _sync_practice_groups to fail and assert that
no unsafe active release survives.
