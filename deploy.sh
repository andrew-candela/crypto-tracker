#!/bin/bash
set -euo pipefail

prep_deployment_package () {
    # Prepare the deployment package
    original_wd=`pwd`
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    pip install .
    deactivate
    cd venv/lib/python3.7/site-packages
    zip -r9 -q ${original_wd}/function.zip .
    cd ${original_wd}

    # Upload the deployment package
    # aws s3 cp function.zip s3://${ZIP_FILE_BUCKET}/${ZIP_FILE_KEY}
    echo "running s3 cp function"
    aws s3 cp function.zip s3://apc-tf/${ZIP_FILE_KEY}
}

deploy () {
    echo "Updating code for function ${1}"
    aws lambda update-function-code \
        --function-name ${1} \
        --s3-bucket ${ZIP_FILE_BUCKET} \
        --s3-key ${ZIP_FILE_KEY}
}

main () {
    prep_deployment_package
    for lambda_function in crypto_batch 
                        #    crypto_email \
                        #    crypto_metrics
    do
        deploy $lambda_function
    done
}

main
