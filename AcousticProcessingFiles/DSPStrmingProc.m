%% This script runs real time processing such that the recorded audio is 
%  all used to determine whether a dementia patient is agitated. The
%  envelope of the signal is sampled at 100 Hz, and the Teager energy of 
%  resultant waveform was found. The Teager energy is window-averaged,
%  after which a threshold is applied. The thresholding separates detected
%  from un-agitated periods of time. 
close all

%Initialize the recording hardware
windowSize = 16384;
recorder = dsp.AudioRecorder('SampleRate',8000,'SamplesPerFrame',...
    windowSize);
Fs = recorder.SampleRate;
currentT = 0:1/100:500/100-1/100;
prevT = 0;
t = 0:1/100:10000/100-1/100;

%Make the filters that are needed for the band pass filtering
% Bandpass 60-4000 Hz
d = fdesign.bandpass('N,F3dB1,F3dB2',2,60,4000,Fs);
bandpass = design(d,'butter');
%fvtool(Hd)


while(1)
    figure(1)
    xlim([0 2102400])
    hold on
    
    figure(2)
    xlim([0 2102400])
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
        wnAvg  = winAvg(tgrEnv, 128);
        figure(1)
        plot(tTgr',wnAvg, 'r');
        figure(2)
        plot(tEnv', envIn(:,1), 'b')
        drawnow
        count = count + 1;
    end
    close all
end