#!/bin/sh

# Define the directory containing the files to be processed
files_dir="/path/to/your/files"

# Function to decode a base64-encoded value
decode_base64() {
  echo "$1" | base64 -d
}

# Loop through the files in the directory
for file in $files_dir/*; do
  if [ -f "$file" ]; then
    # Iterate through environment variables with the specified prefix
    for var_name in $(printenv | grep 'PREFIX_' | cut -d= -f1); do
      var_value=$(echo "$var_name" | sed 's/PREFIX_//')
      secret_value=$(decode_base64 "$(printenv "$var_name")")
      sed -i "s/{{PREFIX_$var_value}}/$secret_value/g" "$file"
    done
  fi
done

# Sleep to keep the init container running
sleep infinity

#DD_COLLECT_KUBERNETES_EVENTS
