%% This script runs real time processing such that the recorded audio is 
%  all used to determine whether a dementia patient is agitated. The
%  envelope of the signal is sampled at 100 Hz, and the Teager energy of 
%  resultant waveform was found. The Teager energy is window-averaged,
%  after which a threshold is applied. The thresholding separates detected
%  from un-agitated periods of time. 
close all

%Initialize the recording hardware
recorder = dsp.AudioRecorder('SampleRate',44100,'SamplesPerFrame',1024);
Fs = recorder.SampleRate;
currentT = 0:1/100:500/100-1/100;
prevT = 0;
t = 0:1/100:10000/100-1/100;

%Make the filters that are needed for the band pass filtering
[b0,a0] = butter(2,4000/Fs,'low');
[b1,a1] = butter(2,60/Fs,'high');

figure(1)
xlim([0 100])
hold on

tic
Tstop = 100;
count = 0;
while (toc < Tstop)
    audioIn = step(recorder);
    envIn   = envelope(audioIn);
    
    
    
    
%     audioenv = getaudiodata(recorder);
%     %audioenv = filter(b0,a0,filter(b1,a1,audioenv));
%     audioenv = envelope(audioenv, 2048, 'peak');  
%     %This didn't quite make sense in this location, because the envelope, 
%     % almost by definition, has a different set of frequencies associated
%     % with it. However, the alternative messes up the data, i.e. filtering
%     % before the envelope is found messes it up.........
%     audioenv = filter(b0,a0,filter(b1,a1,audioenv));
%     audioenv = decimate(audioenv, 10);
%     audioenv = decimate(audioenv, 8);
%     envteagr = teager(audioenv);
%     envteagr(1:30) = 0;
%     envteagr = winAvg(envteagr, 50);
%     %envteagr = TimeIdentifier(envteagr, 0.2e-07);
%     teagT = currentT(2:length(currentT)-1);
%     plot(teagT, envteagr);
%     currentT = (prevT+500)/100:1/100:(prevT+1000-1)/100;
%     prevT = prevT + 5*Fs/80;
%     if (prevT >= 10000)
%         prevT = 0;
%         currentT = 0:1/100:500/100-1/100;
%         close all
%         figure(1)
%         xlim([0 100])
%         %ylim([-0.0000001 0.0000001])
%         hold on
%     end
end