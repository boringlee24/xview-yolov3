import argparse
import time
from sys import platform
import os
import sys
sys.path.append('../')
user = os.environ.get('USER')
import socket
hostname = socket.gethostname()

parser = argparse.ArgumentParser()
# Get data configuration
if platform == 'darwin':  # macos
    parser.add_argument('--image_folder', type=str, default='/Users/glennjocher/Downloads/DATA/xview/train_images/5.tif')
    parser.add_argument('--output_folder', type=str, default='./output_xview', help='path to outputs')
    cuda = True  # torch.cuda.is_available()
else:  # gcp
    # cd yolo && python3 detect.py -secondary_classifier 1
    parser.add_argument('--image_folder', type=str, default='/work/li.baol/val_images', help='path to images')
    parser.add_argument('--output_folder', type=str, default='../output', help='path to outputs')
    cuda = True

parser.add_argument('--plot_flag', type=bool, default=False)
parser.add_argument('--secondary_classifier', type=bool, default=False)
parser.add_argument('--cfg', type=str, default='cfg/c60_a30symmetric.cfg', help='cfg file path')
parser.add_argument('--class_path', type=str, default='data/xview.names', help='path to class label file')
parser.add_argument('--conf_thres', type=float, default=0.99, help='object confidence threshold')
parser.add_argument('--nms_thres', type=float, default=0.4, help='iou threshold for non-maximum suppression')
parser.add_argument('--batch_size', type=int, default=2, help='size of the batches')
parser.add_argument('--img_size', type=int, default=32 * 51, help='size of each image dimension')
parser.add_argument('--epochs', type=int, default=10, help='number of epochs')
parser.add_argument('--tc', type=str, default='none', help='testcase of hardware')
parser.add_argument('--mps_set', action='store_true', help='enable this if operating in MPS mode', default=False)
parser.add_argument('--mps_pct', type=str, help='thread partition percentage', default='100')
parser.add_argument('--cuda_device', type=str, help='cuda device when running mps', default='0')

opt = parser.parse_args()
print(opt)

if opt.mps_set: 
    os.environ['CUDA_MPS_ACTIVE_THREAD_PERCENTAGE'] = opt.mps_pct
    os.environ['CUDA_MPS_LOG_DIRECTORY']=f'/scratch/{user}/mps_log/nvidia-log-{hostname}/{opt.cuda_device}'
    os.environ['CUDA_MPS_PIPE_DIRECTORY']=f'/scratch/{user}/mps_log/nvidia-mps-{hostname}/{opt.cuda_device}'


from models import *
from utils.datasets import *
from utils.utils import *
import json
os.chdir('../')

targets_path = 'utils/targets_c60.mat'


def detect(opt):
    if opt.plot_flag:
        os.system('rm -rf ' + opt.output_folder + '_img')
        os.makedirs(opt.output_folder + '_img', exist_ok=True)
    os.system('rm -rf ' + opt.output_folder)
    os.makedirs(opt.output_folder, exist_ok=True)
    device = torch.device('cuda:0' if cuda else 'cpu')

    # Load model 1
    model = Darknet(opt.cfg, opt.img_size)
    checkpoint = torch.load('weights/best.pt', map_location='cpu')

    model.load_state_dict(checkpoint['model'])
    model.to(device).eval()
    del checkpoint

    # Load model 2
    if opt.secondary_classifier:
        model2 = ConvNetb()
        checkpoint = torch.load('weights/classifier.pt', map_location='cpu')

        model2.load_state_dict(checkpoint['model'])
        model2.to(device).eval()
        del checkpoint
    else:
        model2 = None

    # Set Dataloader
    classes = load_classes(opt.class_path)  # Extracts class labels from file
    dataloader = ImageFolder(opt.image_folder, batch_size=opt.batch_size, img_size=opt.img_size)

    # prev_time = time.time()
    # detections = None
    # mat_priors = scipy.io.loadmat(targets_path)
    lat_list = []
    preds = []

    for epoch in range(opt.epochs):
        for batch_i, (img_paths, img) in enumerate(dataloader):
            print(batch_i, img.shape, end=' ')

            length = opt.img_size
            ni = int(math.ceil(img.shape[1] / length))  # up-down
            nj = int(math.ceil(img.shape[2] / length))  # left-right
            t_start = time.time()
            for i in range(ni):  # for i in range(ni - 1):
    #            print('row %g/%g: ' % (i, ni), end='')

                for j in range(nj):  # for j in range(nj if i==0 else nj - 1):
    #                print('%g ' % j, end='', flush=True)

                    # forward scan
                    y2 = min((i + 1) * length, img.shape[1])
                    y1 = y2 - length
                    x2 = min((j + 1) * length, img.shape[2])
                    x1 = x2 - length

                    # Get detections
                    with torch.no_grad():
                        # Normal orientation
                        chip = torch.from_numpy(img[:, y1:y2, x1:x2]).unsqueeze(0).to(device)
                        pred = model(chip)
                        pred = pred[pred[:, :, 4] > opt.conf_thres]
                        if len(pred) > 0:
                            pred[:, 0] += x1
                            pred[:, 1] += y1
                            preds.append(pred.unsqueeze(0))

    #        print('Batch %d... (Done %.3fs)' % (batch_i, time.time() - prev_time))
            t_end = time.time()
            lat_list.append(round((t_end - t_start)*1000,3)) # in ms
            print(f'item {batch_i} done')

    with open(f'experiments/logs/{opt.tc}.json', 'w') as f:
        json.dump(lat_list, f, indent=4)

    # Bounding-box colors
    color_list = [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)] for _ in range(len(classes))]

    return

class ConvNetb(nn.Module):
    def __init__(self, num_classes=60):
        super(ConvNetb, self).__init__()
        n = 64  # initial convolution size
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, n, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(n),
            nn.LeakyReLU())
        self.layer2 = nn.Sequential(
            nn.Conv2d(n, n * 2, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(n * 2),
            nn.LeakyReLU())
        self.layer3 = nn.Sequential(
            nn.Conv2d(n * 2, n * 4, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(n * 4),
            nn.LeakyReLU())
        self.layer4 = nn.Sequential(
            nn.Conv2d(n * 4, n * 8, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(n * 8),
            nn.LeakyReLU())
        self.layer5 = nn.Sequential(
            nn.Conv2d(n * 8, n * 16, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(n * 16),
            nn.LeakyReLU())
        # self.layer6 = nn.Sequential(
        #     nn.Conv2d(n * 16, n * 32, kernel_size=3, stride=2, padding=1, bias=False),
        #     nn.BatchNorm2d(n * 32),
        #     nn.LeakyReLU())

        # self.fc = nn.Linear(int(8192), num_classes)  # 64 pixels, 4 layer, 64 filters
        self.fully_conv = nn.Conv2d(n * 16, 60, kernel_size=4, stride=1, padding=0, bias=True)

    def forward(self, x):  # 500 x 1 x 64 x 64
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        # x = self.layer6(x)
        # x = self.fc(x.reshape(x.size(0), -1))
        x = self.fully_conv(x)
        return x.squeeze()  # 500 x 60


if __name__ == '__main__':
    torch.cuda.empty_cache()
    detect(opt)
    torch.cuda.empty_cache()
