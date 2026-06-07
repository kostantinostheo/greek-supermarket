import express from 'express';
import { rateLimit } from 'express-rate-limit'
import swaggerJSDoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';

import apiRouter from './routes/routes.js';
import { swaggerOptions } from './swagger.options.js';

const limiter = rateLimit({
	windowMs: 15 * 60 * 1000, // 15 minutes
	limit: 100,
	standardHeaders: 'draft-8',
	legacyHeaders: false, 
	ipv6Subnet: 56,
})
const app = express();
const PORT = 8000;

app.use(express.json());
app.use(limiter);

const swaggerDocs = swaggerJSDoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocs));

app.use("/api/v1", apiRouter);

app.listen(PORT, () => {
    console.log(`API running at http://localhost:${PORT}`);
});