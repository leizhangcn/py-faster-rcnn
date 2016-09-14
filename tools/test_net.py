#!/usr/bin/env python

# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""Test a Fast R-CNN network on an image database."""

import _init_paths
from fast_rcnn.test import test_net
from fast_rcnn.config import cfg, cfg_from_file, cfg_from_list
from datasets.factory import get_imdb
import caffe
import argparse
import pprint
import time, os, sys

def parse_args(args_list):
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Test a Fast R-CNN network')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU id to use',
                        default=0, type=int)
    parser.add_argument('--def', dest='prototxt',
                        help='prototxt file defining the network',
                        default=None, type=str)
    parser.add_argument('--net', dest='caffemodel',
                        help='model to test',
                        default=None, type=str)
    parser.add_argument('--cfg', dest='cfg_file',
                        help='optional config file', default=None, type=str)
    parser.add_argument('--wait', dest='wait',
                        help='wait until net file exists',
                        default=True, type=bool)
    parser.add_argument('--imdb', dest='imdb_name',
                        help='dataset to test on',
                        default='vehicle', type=str)
    parser.add_argument('--db_path', dest='db_path',
                        help='full path to .db file',
                        required=True)
    parser.add_argument('--comp', dest='comp_mode', help='competition mode',
                        action='store_true')
    parser.add_argument('--set', dest='set_cfgs',
                        help='set config keys', default=None,
                        nargs=argparse.REMAINDER)
    parser.add_argument('--out_db_file', default=':memory:',
                        help='filepath of output database. Default is in-memory')

    if len(args_list) == 0:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(args_list)
    return args

def main(args_list):
    args = parse_args(args_list)

    print('Called with args:')
    print(args)

    if args.cfg_file is not None:
        cfg_from_file(args.cfg_file)
    if args.set_cfgs is not None:
        cfg_from_list(args.set_cfgs)

    cfg.GPU_ID = args.gpu_id

    print('Using config:')
    pprint.pprint(cfg)

    while not os.path.exists(args.caffemodel) and args.wait:
        print('Waiting for {} to exist...'.format(args.caffemodel))
        time.sleep(10)

    if cfg.GPU_ID < 0:
        print 'Setting CPU mode'
        caffe.set_mode_cpu()
        cfg.USE_GPU_NMS = False
    else:
        print 'Setting GPU device %d for training' % cfg.GPU_ID
        caffe.set_mode_gpu()
        caffe.set_device(cfg.GPU_ID)

    net = caffe.Net(args.prototxt, args.caffemodel, caffe.TEST)
    net.name = os.path.splitext(os.path.basename(args.caffemodel))[0]

    imdb = get_imdb(args.imdb_name, args.db_path)
    #imdb = get_imdb(args.imdb_name)
    imdb.competition_mode(args.comp_mode)
    if not cfg.TEST.HAS_RPN:
        imdb.set_proposal_method(cfg.TEST.PROPOSAL_METHOD)

    test_net(net, imdb, args.out_db_file)


if __name__ == '__main__':
    '''Wrap train_net in order to call script from python as well as console.'''
    args_list = sys.argv[1:]
    main(args_list)
