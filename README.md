# pycbc-glue repository

This repository contains a stripped down version of lalsuite/glue for use
with PyCBC until the dependencies contained in this repository are retired.

## Notes on repository creation

The repository was created from the 1.48 release (ER7 release) with the 
commands:

    git init
    git remote add -f origin git://ligo-vcs.phys.uwm.edu/lalsuite.git
    git checkout glue-1-48-branch
    git filter-branch --subdirectory-filter glue
    git branch -f master glue-1-48-branch
    git checkout master
    git branch -D glue-1-48-branch
    for t in `git tag` ; do git tag -d $t ; done

The repository was then switched to github with

    git remote rename origin upstream
    git remote add origin git@github.com:ligo-cbc/pycbc-glue.git
    git push -u origin master

