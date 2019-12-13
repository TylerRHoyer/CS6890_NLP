This project has been broken down into multiple scripts for ease of use. At times scripts may fail or stages may not produce desirable results so parameters need to be tweaked. The scripts can be summerized as follows:

gather.py
Uncomment loops to iterate through and gather all of the posts for specific time periods. This process takes about a week with a fast internet connection, there is roughly 1.5 TB of information while compressed.

process.py
This script unpacks the posts and performs the first level of filtering. It filters deleted posts, invalid posts, and non-english posts. It also applies a one keyword matching filter that results in 4M posts if I remember correctly. Be sure to tune the paths to grab data from, the temporary working directory to unpack results into, where to store the filtered files, and the number of processes to use. This script takes many days to run with 32 threads on a 7th generation i9 X series. Initially it is bottlenecked by obtaining the gigbytes of files to process but it seems that processing takes longer than copying the data.

graph.py
This script is no longer needed, but included to give a head start if future researchers would like to implement Baysian networks to find words related to clean energy. Beware: running on the full data set takes over 120 GB of RAM and took about an hour. The results I received were not desirable, so some debugging will need to be done.

filter.lua
This script is written in Lua because LuaJIT is MUCH faster than python for serial tasks. This script takes in the filtered files from process.py and compiles them into a single file. It also performs the full phrase filtering mentioned in the paper. It has an option to subsample the results so that later processes can be tested on smaller samples. Finally, it also orders the data by timestamp. It should be noted that there is some legacy code in here that created data suitable for graph.py, although is no longer used. Runs in seconds. LuaJIT for the win.

LDA.py
This script takes the output from filter.lua and does one of two things with it. filterAll trains multiple LDA models on the filtered corpus results in coherence chart seen in the paper. viewLDA trains a single LDA model and saves it to a file. A run on the full dataset takes roughly 3 days. The multiprocessing version of LDA in the same library may make it twice as fast however doesn't have as many features and so may yield worse results.

sentiments.py
This script takes the output from filter.lua and the LDA model from LDA.py. It uses the VADER sentiment analyser on each sentence and weights the results by each topic. It outputs time.pck (a pickled array of timestamp strings) and sentiments.py (a tensor of sentiments for each post for each topic). Takes about a minute with 32 processes.

train.py
Originally this file was meant to train the neural network however it ended up doing all the preprocessing and creating pretty charts to display the data. The first half performs the windowed mean and finds the standard deviation. The latter half creates the plots of the sentiments over time and the phase plots for comparisons between sentiments. Single process although I've optimized it so it runs in a couple minutes.

nn.py
This script actually trains the neural network, after doing yet more preprocessing. It interpolates the data and trains the network with TFlearn. This is about where I left off so it doesn't save the network but does create some fancy looking graphs to visualize the results.

chart_gen.py
This script creates the illustration graph seen in the poster to describe the goal of the project.

word_3_filtered.txt is the results of filter.lua (the results of process.py were too big to upload). I've also included the times.pck from sentiments.py (sentiments.pck was also too big) and the avg.pck and std.pck from train.py. Finally, I've included some of the graphs for your viewing pleasure. :)