const https = require('https');

module.exports = function (context, req) {
    context.log('Sitemap proxy function triggered');
    
    return new Promise((resolve) => {
        const backendUrl = 'https://tejomag-backend.azurewebsites.net/sitemap.xml';
        
        https.get(backendUrl, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                if (res.statusCode === 200) {
                    context.res = {
                        status: 200,
                        headers: {
                            'Content-Type': 'application/xml; charset=utf-8',
                            'Access-Control-Allow-Origin': '*'
                        },
                        body: data
                    };
                } else {
                    context.res = {
                        status: res.statusCode,
                        body: `Error fetching sitemap: ${res.statusCode}`
                    };
                }
                resolve();
            });
        }).on('error', (error) => {
            context.log.error(`Error: ${error.message}`);
            context.res = {
                status: 500,
                body: `Error: ${error.message}`
            };
            resolve();
        });
    });
};

