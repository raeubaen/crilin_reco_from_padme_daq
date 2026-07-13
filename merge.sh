#!/bin/bash

# Usage: ./merge.sh filelist.txt output.root TreeName
LISTFILE="$1"
OUTFILE="$2"
TREENAME="$3"

if [[ -z "$LISTFILE" || -z "$OUTFILE" || -z "$TREENAME" ]]; then
    echo "Usage: $0 filelist.txt output.root TreeName"
    return 1
fi

root -l <<EOF
{
    std::ifstream in("$LISTFILE");
    if (!in.is_open()) {
        std::cerr << "ERROR: cannot open file list: $LISTFILE" << std::endl;
        return;
    }

    TChain chain("$TREENAME");

    std::string filename;
    while (std::getline(in, filename)) {
        if (filename.size() == 0) continue;
        std::cout << "Adding: " << filename << std::endl;
        chain.Add(filename.c_str());
    }

    if (chain.GetListOfFiles()->GetEntries() == 0) {
        std::cerr << "ERROR: no files found in list. Exiting." << std::endl;
        return;
    }

    std::cout << "Merging into: $OUTFILE" << std::endl;
    chain.Merge("$OUTFILE");

    std::cout << "Done." << std::endl;
}
EOF
