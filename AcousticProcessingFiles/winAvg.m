function [avgs] = winAvg(sig, win)

%% function [avgs] = winAvg(sig, win) takes the avg over a specified window
%  with a 50% overlap. 
avgs = sig;
avgs(avgs ~= 0) = 0;
for n = (win/2 +1): (win/2) : (length(sig) - win/2)
    avgs((n - win/2) : (n + win/2)) = mean(sig(n-win/2:n+win/2));
end