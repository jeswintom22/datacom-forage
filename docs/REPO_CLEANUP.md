# Repository Cleanup (History Rewriting)

What I did

- Removed large/unwanted binary files from repository history using `git-filter-repo` on a fresh mirror clone.
- Patterns removed: `*.pptx`, `*.ppt`, `*.db`, `apps/api/*.db`, `*.exe`, `*.msi`, `*.dll`, `*.class`, `*.key`, `*.odp`.
- Force-pushed the cleaned history to `origin` to replace the previous history.

Why

- Large binary files increase repo size and slow clones. These files are typically build artifacts or user uploads that should be stored outside Git.

Backup

- Before rewriting history I created a backup branch in the original local repository named `backup-before-filter-20260527225450`.
  - This branch points to the unfiltered history and can be used to recover any accidentally removed content.

Commands run (summary)

1. Create a mirror clone and run filter-repo there (mirror keeps all refs):

```bash
cd /path/to/workspace
git clone --mirror https://github.com/jeswintom22/datacom-forage.git datacom-filter-repo.git
cd datacom-filter-repo.git
git filter-repo --invert-paths --path-glob '*.pptx' --path-glob '*.ppt' --path-glob '*.db' --path-glob 'apps/api/*.db' --path-glob '*.exe' --path-glob '*.msi' --path-glob '*.dll' --path-glob '*.class' --path-glob '*.key' --path-glob '*.odp' --force
git remote add origin https://github.com/jeswintom22/datacom-forage.git
git push --mirror --force
```

2. Locally (original clone) I created a backup branch before doing the rewrite:

```bash
git branch backup-before-filter-$(date +%Y%m%d%H%M%S)
```

3. After pushing the cleaned history I updated the local working tree to match the new remote:

```bash
git fetch origin
git reset --hard origin/main
```

What changed

- The repository history on the remote has been rewritten; commits that contained the removed files no longer reference those blobs.
- Repository size should be reduced; however, GitHub may take some time to show the size change.

Important notes for collaborators

- This rewrite is destructive to commit history. All collaborators must re-clone the repository or reset their local branches to match the new remote.

Options:

- Preferred (recommended): reclone repository fresh:

```bash
git clone https://github.com/jeswintom22/datacom-forage.git
```

- Or, if not possible, reset your local branches (dangerous if you have local commits):

```bash
git fetch origin
git checkout main
git reset --hard origin/main
```

Recovering removed content

- If you need any data from the pre-filter history, check out the backup branch `backup-before-filter-20260527225450` from the machine where it exists (I created it locally). If you no longer have access to that machine, we can fetch it from a temporary remote I can push if requested.

Questions / Next steps

- If you want, I can remove additional patterns, purge other sensitive files, or help coordinate notifying collaborators and rotating any credentials that may have been exposed in the old history.
