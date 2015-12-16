%% Extract Teager energy over time.

function [TE] = teager(sig)
TE = 2:1:length(sig)-2;

for n = 2:1:(length(sig)-2)
    TE(n) = abs(sig(n))^2 - sig(n+1)*conj(sig(n-1));
end