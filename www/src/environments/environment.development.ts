export const environment = {
    production: false,
    apiUrl: 'http://localhost:8080/',
    timeFormat: 'hh:mm a',
    locale:'en-US',
    //How often the panels ask the backend for fresh trends. The state log only gets a new row
    //every few minutes, so there is nothing to gain by asking more often than this.
    trendRefreshMinutes: 5
};
