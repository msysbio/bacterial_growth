#! /usr/bin/gawk -f

# Author: 
#    Savvas Paragkamian
# Aim:
#   This script creates a tsv file with all the NCBI ids that correspond to unicellular taxa.
# 
# Usage:
#   ./filter_unicellular_ncbi.awk \
#       METdb_GENOMIC_REFERENCE_DATABASE_FOR_MARINE_SPECIES.csv database_groups.tsv > growthDB_unicellular_ncbi.tsv


BEGIN {

    ## Two conditional field separators. CAREFUL! 
    FS="[\t,]"

    ## Bacteria and Archaea
    selected_microbe_high_level_taxa[2]=1;      # tax id 2 stands for Bacteria
    selected_microbe_high_level_taxa[2157]=1;   # tax id 2157 stands for Archea

    ## Unicellular Eukaryotes

    ## From supergroup Excavata

    selected_microbe_high_level_taxa[5719]=1;   # tax id 5719 stands for phylum Parabasalia
    selected_microbe_high_level_taxa[5738]=1;   # tax id 5738 stands for order Diplomonadida
    selected_microbe_high_level_taxa[66288]=1;   # tax id 66288 stands for order Oxymonadida
    selected_microbe_high_level_taxa[193075]=1;   # tax id 193075 stands for family Retortamonadidae
    selected_microbe_high_level_taxa[2611341]=1;   # tax id 2611341 stands for clade Metamonada
    selected_microbe_high_level_taxa[207245]=1;   # tax id 207245 stands for plylum Fornicata
    selected_microbe_high_level_taxa[136087]=1;   # tax id 136087 stands for family Malawimonadidae
    selected_microbe_high_level_taxa[85705]=1;   # tax id 85705 stands for family Ancyromonadidae
    selected_microbe_high_level_taxa[1294546]=1;   # tax id 1294546 stands for family Planomonadidae


    ### From supergroup Excavata, clade Discoba (Discristates)
    selected_microbe_high_level_taxa[33682]=1;   # tax id 2157 stands for phylum Euglenozoa
    selected_microbe_high_level_taxa[5752]=1;   # tax id 5752 stands for phylum Heterolobosea (includes Percolomonadidae)
    selected_microbe_high_level_taxa[556282]=1;   # tax id 556282 stands for order Jakobida
    selected_microbe_high_level_taxa[2711297]=1;   # tax id 2711297 stands for order Tsukubamonadida

    ## From supergroup Archaeplastida

    selected_microbe_high_level_taxa[38254]=1;   # tax id 38254 stands for class Glaucocystophyceae
    
    ### Rhodophycea, red algae
    selected_microbe_high_level_taxa[265318]=1;   # tax id 265318 stands for order Cyanidiales
    selected_microbe_high_level_taxa[2798]=1;   # tax id 2798 stands for order Porphyridiales
    selected_microbe_high_level_taxa[661027]=1;   # tax id 661027 stands for class Rhodellophyceae
    selected_microbe_high_level_taxa[446134]=1;   # tax id 446134 stands for class Stylonematophyceae

    ## From Chloroplastida / Viridiplantae
    selected_microbe_high_level_taxa[3166]=1;   # tax id 3166 stands for class Chloropphyceae
    selected_microbe_high_level_taxa[2201463]=1;   # tax id 2201463 stands for class Palmophyllophyceae, synonym of Prasinophyceae
    selected_microbe_high_level_taxa[3166]=1;   # tax id 3166 stands for class Chloropphyceae
    selected_microbe_high_level_taxa[3166]=1;   # tax id 3166 stands for class Chloropphyceae

    ## From Chromalveolata

    ### Alveolata
    
    selected_microbe_high_level_taxa[2864]=1;   # tax id 2864 stands for class Dinophyceae
    selected_microbe_high_level_taxa[5794]=1;   # tax id 5794 stands for class Apicomplexa
    selected_microbe_high_level_taxa[5878]=1;   # tax id 5878 stands for phylum Ciliophora

    ### Stramenopiles
 
    selected_microbe_high_level_taxa[238765]=1;   # tax id 238765 stands for class Actinophryidae
    selected_microbe_high_level_taxa[33849]=1;   # tax id 33849 stands for class Bacillariophyceae
    selected_microbe_high_level_taxa[35131]=1;   # tax id 35131 stands for class Labyrinthulomycetes
    selected_microbe_high_level_taxa[33651]=1;   # tax id 33651 stands for order Bicosoecida

    ### Chromobionta
    selected_microbe_high_level_taxa[2833]=1;   # tax id 2833 stands for class Xanthophyceae
    selected_microbe_high_level_taxa[38410]=1;   # tax id 38410 stands for class Raphidophyceae
    selected_microbe_high_level_taxa[157124]=1;   # tax id 157124 stands for class Pinguiophyceae
    selected_microbe_high_level_taxa[33849]=1;   # tax id 33849 stands for class Bacillariophyceae
    selected_microbe_high_level_taxa[589449]=1;   # tax id 589449 stands for class Mediophyceae
    selected_microbe_high_level_taxa[33836]=1;   # tax id 33836 stands for class Coscinodiscophyceae
    selected_microbe_high_level_taxa[91989]=1;   # tax id 91989 stands for class Bolidophyceae
    selected_microbe_high_level_taxa[35675]=1;   # tax id 35675 stands for class Pelagophyceae
    selected_microbe_high_level_taxa[2825]=1;   # tax id 2825 stands for class Chrysophyceae
    selected_microbe_high_level_taxa[33859]=1;   # tax id 33859 stands for class Synurophyceae
    selected_microbe_high_level_taxa[557229]=1;   # tax id 557229 stands for class Synchromophyceae
    selected_microbe_high_level_taxa[2825]=1;   # tax id 2825 stands for class Chrysophyceae
    selected_microbe_high_level_taxa[39119]=1;   # tax id 39119 stands for class Dictyochophyceae

    ### Haptophyta
    selected_microbe_high_level_taxa[2830]=1;   # tax id 2830 stands for class Haptophyta

    ## Unikonts

    ### Opistrhokonta

    selected_microbe_high_level_taxa[127916]=1;   # tax id 127916 stands for class Ichthyosporea (Mesomycetozoa)
    selected_microbe_high_level_taxa[6029]=1;   # tax id 6029 stands for class Microsporidia (unicellular Fungi)
    selected_microbe_high_level_taxa[4890]=1;   # tax id 4890 stands for phylum Ascomycota (they contain some multicellular)
    selected_microbe_high_level_taxa[28009]=1;   # tax id 28009 stands for class Choanoflagellata

    ### Amoebozoa
    
    selected_microbe_high_level_taxa[555369]=1;   # tax id 555369 stands for phylum Tubulinea (Lobosea)
    selected_microbe_high_level_taxa[555406]=1;   # tax id 555406 stands for clade Archamoebae
    selected_microbe_high_level_taxa[142796]=1;   # tax id 142796 stands for class Mycetozoa (Eumycetozoa, they contain some multicellular)

    ## Cryptobionta

    selected_microbe_high_level_taxa[3027]=1;   # tax id 3027 stands for class Cryptophyceae
    selected_microbe_high_level_taxa[339960]=1;   # tax id 339960 stands for order Kathablepharidacea
    selected_microbe_high_level_taxa[419944]=1;   # tax id 419944 stands for phylum Picozoa

    ## Rhizaria
    
    selected_microbe_high_level_taxa[543769]=1;   # tax id 543769 stands for clade Rhizaria

}
# Load the METdb A GENOMIC REFERENCE DATABASE FOR MARINE SPECIES data in associative array.
(ARGIND==1 && NR>1){
    
    gsub(/"/,"",$10)
    selected_microbe_high_level_taxa[$10]=1;

}
# load the database_groups.tsv from the dictionary
# and check if parent microbes are in the selected_microbe_high_level_taxa
# and print keep the children column (second)
(ARGIND==2 && $1==-2){

    all_taxa[$2]=1;

    if ($4 in selected_microbe_high_level_taxa){

        microbe_taxa[$2]=1;

        }

}
END{

    # Print all taxa if and only if they are included in the microbe taxa array.
    for (tax_id in all_taxa){

        if (tax_id in microbe_taxa){

            print tax_id;

        }
    }
    # Print the ids for the parent taxa of unicellular microbes
    for (selected_microbes in selected_microbe_high_level_taxa){

        print selected_microbes;

    }
}
