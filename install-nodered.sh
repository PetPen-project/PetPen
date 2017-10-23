#!/bin/bash

pushd nodered

modules=`ls`
for i in $modules
do
    pushd $i
    npm link
    popd
done

popd


