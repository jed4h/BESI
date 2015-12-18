%% This script runs real time processing such that the recorded audio is 
%  all used to determine whether a dementia patient is agitated. The
%  envelope of the signal is sampled at 100 Hz, and the Teager energy of 
%  resultant waveform was found. The Teager energy is window-averaged,
%  after which a threshold is applied. The thresholding separates detected
%  from un-agitated periods of time. 
close all

%Initialize the recording hardware
windowSize = 4096;
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

%Make the filters that are needed for the band pass filtering
% Bandpass 60-4000 Hz
d = fdesign.bandpass('N,F3dB1,F3dB2',2,60,4000,Fs);
bandpass = design(d,'butter');
%fvtool(Hd)


while(1)
%     figure(1)
%     xlim([0 windowSize*500])
%     hold on
%     
    figure(2)
    xlim([0 100])
    hold on
    
    figure(3)
    xlim([0 100])
    hold on

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
        runavg = runsum / endOfBuffer;
        
        if buffcount == 1
           if buffer(buffcount) > buffer(endOfBuffer)
              DerivativeCount = DerivativeCount + 1; 
           elseif buffer(buffcount) < buffer(endOfBuffer)
              DerivativeCount = DerivativeCount - 1; 
           end
        else 
           if buffer(buffcount) > buffer(buffcount - 1) 
               DerivativeCount = DerivativeCount + 1; 
           elseif buffer(buffcount) < buffer(buffcount - 1)
              DerivativeCount = DerivativeCount - 1; 
           end
        end
        
        if DerivativeCount > 20 && runavg > 0.02
           currentlyAgitated = 1; 
        end
%         wnAvg  = winAvg(tgrEnv, 128);
        
        figure(3)
        stem(count, runavg, 'b');
        stem(count, buffer(buffcount), 'r:');
%         figure(1)
%         plot(tTgr', wnAvg , 'r');
        figure(2)
        stem(count, currentlyAgitated, 'g')
        drawnow
        
        if buffcount >= 50
            buffcount = 1;
        else
            buffcount = buffcount + 1;
        end
        count = count + 1;
    end
    close all
end