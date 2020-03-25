#!/bin/bash

. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

data=/data1/junyi/disk2/kaldi/egs/aishell/s5/data
test_sets="test_own"
data_sets=test_game_data
online_affix=
affix=
dir=exp/chain/tdnn_1a
dir=${dir}${affix:+_$affix}_sp
online_affix=
nnet3_affix=
iter=final

# Data Preparation,
local/aishell_data_prep_own.sh $data/${data_sets}/wavs $data/${data_sets}/transcript || exit 1;

for datadir in ${test_sets}; do
   utils/copy_data_dir.sh data/$datadir data/${datadir}_hires$online_affix
done

mfccdir=mfcc
for x in ${test_sets}; do
  steps/make_mfcc_pitch.sh --cmd "$train_cmd" --nj 1 data/$x exp/make_mfcc/$x $mfccdir || exit 1;
  steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir || exit 1;
  utils/fix_data_dir.sh data/$x || exit 1;
done

mfccdir=mfcc_perturbed_hires$online_affix
for datadir in ${test_sets}; do
    steps/make_mfcc_pitch$online_affix.sh --nj 1 --mfcc-config conf/mfcc_hires.conf \
      --cmd "$train_cmd" data/${datadir}_hires$online_affix exp/make_hires/$datadir $mfccdir || exit 1;
    steps/compute_cmvn_stats.sh data/${datadir}_hires$online_affix exp/make_hires/$datadir $mfccdir || exit 1;
    utils/fix_data_dir.sh data/${datadir}_hires$online_affix || exit 1;
    # create MFCC data dir without pitch to extract iVector
    utils/data/limit_feature_dim.sh 0:39 data/${datadir}_hires$online_affix data/${datadir}_hires_nopitch || exit 1;
    steps/compute_cmvn_stats.sh data/${datadir}_hires_nopitch exp/make_hires/$datadir $mfccdir || exit 1;
done

for data in $test_sets; do
    steps/online/nnet2/extract_ivectors_online_own.sh --cmd "$train_cmd" --nj 1 \
      data/${data}_hires_nopitch exp/nnet3${nnet3_affix}/extractor \
      exp/nnet3${nnet3_affix}/ivectors_${data}
done
# test_set = "test_own"
graph_dir=$dir/graph
for test_set in $test_sets; do
    steps/nnet3/decode_own.sh --acwt 1.0 --post-decode-acwt 10.0 \
      --nj 1 --cmd "$decode_cmd" --iter ${iter} \
      --online-ivector-dir exp/nnet3/ivectors_${test_set} \
      $graph_dir data/${test_set}_hires $dir/decode_${test_set} || exit 1;
done

# for x in exp/chain/tdnn_1a_sp/decode_test_own; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; done
