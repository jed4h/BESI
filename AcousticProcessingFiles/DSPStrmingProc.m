%% This script runs real time processing such that the recorded audio is 
%  all used to determine whether a dementia patient is agitated. The
%  envelope of the signal is sampled at 100 Hz, and the Teager energy of 
%  resultant waveform was found. The Teager energy is window-averaged,
%  after which a threshold is applied. The thresholding separates detected
%  from un-agitated periods of time. 
close all

%Initialize the recording hardware
windowSize = 1024*4;
recorder = dsp.AudioRecorder('SampleRate',8000,'SamplesPerFrame',...
    windowSize);
Fs = recorder.SampleRate;
currentT = 0:1/100:500/100-1/100;
prevT = 0;
t = 0:1/100:10000/100-1/100;

%Make circular buffer to keep average energy
runsum = 0;
endOfBuffer = 50;
buffer = zeros(endOfBuffer,1);
buffcount = 1;
runavg = 0;
prevRunAvg = 0;

%Need another buffer to store several runavg values in order to figure out
%when to reset the DerivativeCount if there is an ongoing conversation
avgBuffer = zeros(15,1);
avgCount = 1;

%If the person starts to get agitated, then likely the derivative of the
%average energy (graphed in blue in Fig 3) is going to be positive for a
%while, because presumably they are are not going to be agitated for only a
%second. Given this, the only thing we really care about is when the moving
%average has a positive slope. At the same time, we want to make sure that
%the positive slope is above some minimum, because a silent room in which a
%conversation starts will have a positive derivative as well. For now, what
%is being implemented is a count of how long the derivative stays positive.
DerivativeCount = 0;

%Variable indicating current state of person
currentlyAgitated = 0;

Threshold = 0.005;

%Make the filters that are needed for the band pass filtering
% Bandpass 60-4000 Hz
d = fdesign.bandpass('N,F3dB1,F3dB2',2,60,4000,Fs);
bandpass = design(d,'butter');
%fvtool(Hd)

figure(4)
subplot(2,1,1)
xlim([0 700])
title('Average Teager Energy Over Time')
xlabel('Time')
ylabel('Teager Energy')
hold on


subplot(2,1,2)
xlim([0 700])
ylim([-0.1 1.1])
xlabel('Time')
ylabel('Agitation State')
title('Agitation State Corresponding to Time')
hold on


while(1)
%     figure(1)
%     xlim([0 windowSize*500])
%     hold on
%     


    tic

    Tstop = 300;
    count = 0;

    while (toc < Tstop)        
        audioIn = step(recorder);
        audioIn = filter(bandpass,audioIn);
        envIn  = envelope(audioIn);
        %envIn  = envelope(envIn);
        
        tTgr = count*windowSize+2:1:(count+1)*windowSize-1;
        tEnv = count*windowSize+1:1:(count+1)*windowSize;
        tgrEnv = teager(envIn(:,1));
        
        runsum = runsum - buffer(buffcount);
        buffer(buffcount) = mean(tgrEnv);
        runsum = runsum + buffer(buffcount);
        prevRunAvg = runavg;
        runavg = runsum / endOfBuffer;
        avgBuffer(avgCount) = runavg;
        avgCount = avgCount + 1;
        if avgCount > 15
            avgCount = 1;
        end
        
        
        
        if runavg > Threshold
%             if runavg > prevRunAvg
%                 DerivativeCount = DerivativeCount + 1; 
%             end
            if (runavg-prevRunAvg) > 0.00005
                DerivativeCount = DerivativeCount + 1;
            end
            
            if DerivativeCount > 15
                currentlyAgitated = 1; 
            else
%                 DerivativeCount = 0;
                currentlyAgitated = 0;
            end
        end
        
        if abs(runavg-prevRunAvg) <= 0.00005 || runavg < prevRunAvg
            DerivativeCount = DerivativeCount - 1; 
        end
        
        if DerivativeCount < 0 || runavg < Threshold
           DerivativeCount = 0; 
        end
            

%         wnAvg  = winAvg(tgrEnv, 128);
        
        subplot(2,1,1)
        stem(count, runavg, 'b');
        stem(count, buffer(buffcount), 'r:');
        legend('50 Averaged Average Points', '4096 Averaged Samples')
%         figure(1)
%         plot(tTgr', wnAvg , 'r');
        subplot(2,1,2)
        stem(count, currentlyAgitated, 'g')
        drawnow
        
        
        if buffcount >= 50
            buffcount = 1;
        else
            buffcount = buffcount + 1;
        end
        count = count + 1;
        
        (runavg-prevRunAvg)
        DerivativeCount
    end
    
    clf
    
    subplot(2,1,1)
    xlim([0 700])
    title('Average Teager Energy Over Time')
    xlabel('Time')
    ylabel('Teager Energy')
    hold on

    subplot(2,1,2)
    xlim([0 700])
    ylim([-0.1 1.1])
    xlabel('Time')
    ylabel('Agitation State')
    title('Agitation State Corresponding to Time')
    hold on
end