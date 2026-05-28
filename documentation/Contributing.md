# How to contribute to this repo
> Updated: 21st of May 2026

# Quick `git` intro

## `git log` is your friend

**Example output:**
```
commit bdc70832bde6394006411c37a9e74a12cc1833ca (HEAD -> squash, ozer/humble, origin/humble, origin/HEAD, humble)
Author: TheNorthLynx <76127916+TheNorthLynx@users.noreply.github.com>
Date:   Thu May 21 09:11:46 2026 +0200

    CBF obstacle avoidance (#331)
    
```
**Deciphering the output:**
- `commit bdc...3ca ...` is the commit identifier. The long string is universally unique. You can `git checkout` a commit.
- `(HEAD ...` means your files are currently at this commit
- `(HEAD -> squash)` means the branch `squash` is at this commit, and your HEAD is pointing to it.
  - Any new commits will be added to `squash`.
  - HEAD _can_ point at _just_ a commit.
  - You move your HEAD usually via `git checkout <branch/commit>`
- `(HEAD -> squash, ozer/humble, origin/humble, origin/HEAD, humble)` means
  - The branch `humble` of remote repo named `ozer` is also at this commit.
  - The branch `humble` and HEAD of the remote repo named `origin` is also at this commit.
  - The local branch `humble` is also at this commit.
  - Any of these parts could be spread over different commits.
  - All 5 of these options are valid `git checkout` targets.
- Followed by Author, Date and and commit messages
- This structure repeats, with the newest commits on top.
  - Press `q` to quit `git log`
  - Arrow down/page down can shows more.


## Common operations
- `git add <file> <file> ...` adds modified files to the "staging area".
  - `git add .` is convenient, and almost always **WRONG**. Details omitted here.
- `git status` shows you modified and staged files. **Always check before comitting.** Undoing a commit is annoying.
- `git commit` creates a commit from the changes you staged with `git add` on the branch you are currently on.
- `git branch` shows your local branches.
- `git remote` shows github repositories you have added. `git remote -v` will show you the URLs of each remote as well.
- `git fetch <remote>` will download the current state of the remote into your machine, but not modify any files.
- `git merge <branch_X>` will merge the local `<branch_X>` into your current branch. `git merge <remote>/<branch>` works the same way.
- `git pull <remote>/<branch>` is a shortcut for `git fetch <remote>`, `git merge <remote>/<branch>`
- `git push <remote><branch>` "runs" `git pull <your_local_pc>/<branch>` on github's server.
  - Anything you pushed, you should think of as permanently available online. 
  - Always check `git status` before you push. **ALWAYS**.
  - If using a GUI for git, LEARN TO USE IT.
- `git clone <url>`:
  - Downloads the repo.
  - Creates a remote `origin`
  - Creates a local branch according to the repo's default branch setting (`humble` for smarc2).
  - Checks out this local branch. `(HEAD -> <branch>)`
  - Sets this local branch to track the remote branch



## `smarc2` only has one branch, `humble`. 
- Only few people have access to this repo.
- We might move to `jazzy` one day. Maybe when Orins get it.



## The "happy path"

### A) 1-time setup
- On github, fork smarc2 to your account
- `git clone <smarc2 url>`
- `git remote add <YOUR_NAME> <MY FORK URL>`

### B) Repeat for features
- `git checkout humble`
- `git pull origin humble`
- `git branch <my_amazing_feature>`
- `git checkout <my_amazing_feature>`

### C) Repeat as you work
- Do excellent, world-changing work
- `git add <the files i modified>`
- `git commit -m "I modified these things"`
- `git push <YOUR_NAME>/<my_amazing_feature>`

### D) Once happy with work
- On github, make a pull request (PR) from `YOUR_NAME/my_amazing_feature` into `smarc2/humble`
- People that can merge your PR will get an email about this usually. You can also bother them on slack (usually Niklas or Ozer)
- `smarc2` maintainers will _squash_ and merge your PR.
- You optionally delete `my_amazing_feature` branch (`git branch -D my_amazing_feature`)
- Go to B.

## "I see previously merged commits in my new PR?"
- You probably did not make a new branch for your new PR.
- This is a side-effect of _squashed merges_.
- This is what happened:
```
Fresh clone + new work
SMARC2/humble   : Commit X, Y, Z
YOUR_FORK/humble: Commit X, Y, Z, A, B, C

PR MADE from YOUR_FORK/humble to SMARC2/humble
Commits A, B, C are squashed into a new unique commit Q that contains all changes from A, B, C.
SMARC2/humble   : Commit X, Y, Z,          Q
YOUR_FORK/humble: Commit X, Y, Z, A, B, C
Q's commit message is a list of A, B, C's commit messages.

You pulled SMARC2/humble into YOUR_FORK/humble
SMARC2/humble   : Commit X, Y, Z,          Q
YOUR_FORK/humble: Commit X, Y, Z, A, B, C, Q

Did some work
SMARC2/humble   : Commit X, Y, Z,          Q
YOUR_FORK/humble: Commit X, Y, Z, A, B, C, Q, D, E, F
Made a new PR. Look at the difference of commits between your fork and smarc2. Although the files are identical at the point where they share the commit Q, the _A, B, C commits themselves_ are "new" to smarc2, AGAIN.
If a new squash R is made now, it will contain the commit messages from A to F and be annoying.
```

**Why even squash?**

Because we are many.

Normal merges from so many people make the `smarc2` git log useless, since there are SO MANY commits from many people. Hard to tell what got changed and when.

"I need to check if things worked before Ozer merged Jasons shitty PR" is possible to do locally by anyone when we squash PRs, since each PR is one commit this way. Without squashing, this functionality is only really available (semi-conveniently at least) to the mergers.
