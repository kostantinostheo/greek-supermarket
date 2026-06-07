export const swaggerOptions = {
    swaggerDefinition: {
        openapi: '3.0.0',
        info: {
            title: 'Greek Market API',
            version: '0.0.1',
            description: 'API for fetching and processing product data from the Greek market. Supports pagination, sorting, and filtering of products.',
        },
        servers: [
            {
                url: `http://localhost:8000/api/v1`, // Update with your server URL
            },
        ],
   components: {
 },
    },
    apis: ['./routes/*.js'], 
};