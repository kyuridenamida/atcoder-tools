#!/usr/bin/env bash

copy_file(){
    echo "Copying $1 to $2"
    cp $1 $2 -R
}
auto_gen_dir=./src/auto_generated/
# rm -r ${auto_gen_dir}
mkdir -p ${auto_gen_dir}

copy_file ../README.md ${auto_gen_dir}

echo "Done. Please run \`build_data.sh\` as well"
python3 ./copy_default_templates.py > ${auto_gen_dir}/templateData.js
python3 ./copy_readme_template_section.py > ${auto_gen_dir}/README_TEMPLATE_SECTION.md
python3 ./copy_ts_model_definition.py > ${auto_gen_dir}/qualityResultDefinition.js

quality_result_path=./src/auto_generated/qualityResultList.js
json_path=./data_builder/out/all_data.json
echo "creating ${quality_result_path}"
echo "Please run \`build_data.sh\` if you get an error or you would like to update the data."
echo -n "export default " > ${quality_result_path}
cat ${json_path} >> ${quality_result_path}
echo ";" >> ${quality_result_path}
mkdir ./public/api/ -p
cp ${json_path} ./public/api/all.json
