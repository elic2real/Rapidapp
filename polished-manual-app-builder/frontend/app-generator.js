import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import archiver from 'archiver';
import { TemplateEngine } from './template-engine.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class AppGenerator {
    constructor() {
        this.appsDir = path.join(__dirname, '../generated-apps');
        this.generationStatus = new Map();
        this.templateEngine = new TemplateEngine();
        
        // Ensure apps directory exists
        this.ensureAppsDirectory();
    }

    async ensureAppsDirectory() {
        try {
            await fs.access(this.appsDir);
        } catch {
            await fs.mkdir(this.appsDir, { recursive: true });
        }
    }

    async generateApp(appId, appSpec) {
        this.generationStatus.set(appId, {
            status: 'generating',
            progress: 0,
            startTime: new Date(),
            spec: appSpec
        });

        try {
            const appDir = path.join(this.appsDir, appId);
            await fs.mkdir(appDir, { recursive: true });

            // Generate based on stack
            await this.generateByStack(appDir, appSpec);

            this.generationStatus.set(appId, {
                ...this.generationStatus.get(appId),
                status: 'completed',
                progress: 100,
                completedTime: new Date()
            });

            console.log(`✅ App generation completed: ${appId}`);

        } catch (error) {
            console.error(`❌ App generation failed: ${appId}`, error);
            this.generationStatus.set(appId, {
                ...this.generationStatus.get(appId),
                status: 'failed',
                error: error.message
            });
            throw error;
        }
    }

    async generateByStack(appDir, appSpec) {
        const { stack } = appSpec;

        switch (stack) {
            case 'nextjs-postgres':
                await this.generateNextJSApp(appDir, appSpec);
                break;
            case 'nextjs-mongodb':
                await this.generateNextJSApp(appDir, appSpec, 'mongodb');
                break;
            case 'nextjs-redis':
                await this.generateNextJSApp(appDir, appSpec, 'redis');
                break;
            case 'fastapi-postgres':
                await this.generateFastAPIApp(appDir, appSpec);
                break;
            case 'vue-postgres':
                await this.generateVueApp(appDir, appSpec);
                break;
            case 'rust-axum-postgres':
                await this.generateRustApp(appDir, appSpec);
                break;
            default:
                await this.generateNextJSApp(appDir, appSpec);
        }
    }

    async generateNextJSApp(appDir, appSpec, dbType = 'postgres') {
        // Create Next.js project structure
        await this.createDirectoryStructure(appDir, [
            'src/app',
            'src/components',
            'src/lib',
            'src/hooks',
            'src/types',
            'public',
            'prisma'
        ]);

        // Generate package.json
        await this.writeFile(appDir, 'package.json', this.templateEngine.generatePackageJson(appSpec, 'nextjs', dbType));

        // Generate Next.js config
        await this.writeFile(appDir, 'next.config.js', this.templateEngine.generateNextConfig(appSpec));

        // Generate Tailwind config
        await this.writeFile(appDir, 'tailwind.config.js', this.templateEngine.generateTailwindConfig());
        await this.writeFile(appDir, 'postcss.config.js', this.templateEngine.generatePostcssConfig());

        // Generate main layout
        await this.writeFile(appDir, 'src/app/layout.tsx', this.templateEngine.generateLayout(appSpec));
        await this.writeFile(appDir, 'src/app/page.tsx', this.templateEngine.generateHomePage(appSpec));
        await this.writeFile(appDir, 'src/app/globals.css', this.templateEngine.generateGlobalCSS(appSpec));

        // Generate pages based on spec
        for (const page of appSpec.pages) {
            if (page.toLowerCase() !== 'home') {
                await this.generatePage(appDir, page, appSpec);
            }
        }

        // Generate components
        await this.generateComponents(appDir, appSpec);

        // Generate database schema
        if (dbType === 'postgres' || dbType === 'mongodb') {
            await this.generateDatabaseSchema(appDir, appSpec, dbType);
        }

        // Generate API routes
        await this.generateAPIRoutes(appDir, appSpec);

        // Generate configuration files
        await this.generateConfigFiles(appDir, appSpec);

        // Generate README
        await this.writeFile(appDir, 'README.md', this.templateEngine.generateREADME(appSpec));
    }

    async generateFastAPIApp(appDir, appSpec) {
        // Create FastAPI project structure
        await this.createDirectoryStructure(appDir, [
            'app',
            'app/api',
            'app/models',
            'app/services',
            'app/core',
            'app/db',
            'tests'
        ]);

        // Generate Python files
        await this.writeFile(appDir, 'requirements.txt', this.templateEngine.generateRequirements(appSpec));
        await this.writeFile(appDir, 'app/main.py', this.templateEngine.generateFastAPIMain(appSpec));
        await this.writeFile(appDir, 'app/core/config.py', this.templateEngine.generateFastAPIConfig(appSpec));
        
        // Generate models and API routes
        for (const entity of appSpec.databaseEntities) {
            await this.writeFile(appDir, `app/models/${entity.toLowerCase()}.py`, this.templateEngine.generatePydanticModel(entity, appSpec));
            await this.writeFile(appDir, `app/api/${entity.toLowerCase()}.py`, this.templateEngine.generateFastAPIRoute(entity, appSpec));
        }

        await this.writeFile(appDir, 'README.md', this.templateEngine.generateREADME(appSpec));
    }

    async generateVueApp(appDir, appSpec) {
        await this.createDirectoryStructure(appDir, [
            'src',
            'src/components',
            'src/views',
            'src/stores',
            'src/router',
            'public'
        ]);

        await this.writeFile(appDir, 'package.json', this.templateEngine.generatePackageJson(appSpec, 'vue'));
        await this.writeFile(appDir, 'src/main.js', this.templateEngine.generateVueMain(appSpec));
        await this.writeFile(appDir, 'src/App.vue', this.templateEngine.generateVueApp(appSpec));
        
        // Generate Vue pages
        for (const page of appSpec.pages) {
            await this.writeFile(appDir, `src/views/${page}.vue`, this.templateEngine.generateVuePage(page, appSpec));
        }

        await this.writeFile(appDir, 'README.md', this.templateEngine.generateREADME(appSpec));
    }

    async generateRustApp(appDir, appSpec) {
        await this.createDirectoryStructure(appDir, [
            'src',
            'src/handlers',
            'src/models',
            'src/db'
        ]);

        await this.writeFile(appDir, 'Cargo.toml', this.templateEngine.generateCargoToml(appSpec));
        await this.writeFile(appDir, 'src/main.rs', this.templateEngine.generateRustMain(appSpec));
        
        for (const entity of appSpec.databaseEntities) {
            await this.writeFile(appDir, `src/models/${entity.toLowerCase()}.rs`, this.templateEngine.generateRustModel(entity, appSpec));
        }

        await this.writeFile(appDir, 'README.md', this.templateEngine.generateREADME(appSpec));
    }

    async generatePage(appDir, pageName, appSpec) {
        const pageDir = `src/app/${pageName.toLowerCase()}`;
        await fs.mkdir(path.join(appDir, pageDir), { recursive: true });
        await this.writeFile(appDir, `${pageDir}/page.tsx`, this.templateEngine.generatePage(pageName, appSpec));
    }

    async generateComponents(appDir, appSpec) {
        const components = this.getRequiredComponents(appSpec);
        
        for (const component of components) {
            await this.writeFile(appDir, `src/components/${component}.tsx`, 
                this.templateEngine.generateComponent(component, appSpec));
        }
    }

    getRequiredComponents(appSpec) {
        const components = ['Header', 'Footer', 'Button', 'Input'];
        
        if (appSpec.authentication) components.push('LoginForm', 'RegisterForm');
        if (appSpec.search) components.push('SearchBar');
        if (appSpec.adminPanel) components.push('AdminPanel', 'DataTable');
        if (appSpec.fileUpload) components.push('FileUpload');
        if (appSpec.realTime) components.push('NotificationToast');
        
        return components;
    }

    async generateDatabaseSchema(appDir, appSpec, dbType) {
        if (dbType === 'postgres') {
            await this.writeFile(appDir, 'prisma/schema.prisma', this.templateEngine.generatePrismaSchema(appSpec));
        } else if (dbType === 'mongodb') {
            await this.writeFile(appDir, 'src/lib/mongodb.ts', this.templateEngine.generateMongoSchema(appSpec));
        }
    }

    async generateAPIRoutes(appDir, appSpec) {
        const apiDir = 'src/app/api';
        
        for (const entity of appSpec.databaseEntities) {
            const entityDir = `${apiDir}/${entity.toLowerCase()}`;
            await fs.mkdir(path.join(appDir, entityDir), { recursive: true });
            await this.writeFile(appDir, `${entityDir}/route.ts`, this.templateEngine.generateAPIRoute(entity, appSpec));
        }

        if (appSpec.authentication) {
            const authDir = `${apiDir}/auth`;
            await fs.mkdir(path.join(appDir, authDir), { recursive: true });
            await this.writeFile(appDir, `${authDir}/route.ts`, this.templateEngine.generateAuthAPI(appSpec));
        }
    }

    async generateConfigFiles(appDir, appSpec) {
        // Environment variables
        await this.writeFile(appDir, '.env.local', this.templateEngine.generateEnvFile(appSpec));
        await this.writeFile(appDir, '.env.example', this.templateEngine.generateEnvExample(appSpec));
        
        // TypeScript config
        await this.writeFile(appDir, 'tsconfig.json', this.templateEngine.generateTSConfig());
        
        // ESLint config
        await this.writeFile(appDir, '.eslintrc.json', this.templateEngine.generateESLintConfig());
        
        // Git ignore
        await this.writeFile(appDir, '.gitignore', this.templateEngine.generateGitignore());
    }

    async createDirectoryStructure(appDir, directories) {
        for (const dir of directories) {
            await fs.mkdir(path.join(appDir, dir), { recursive: true });
        }
    }

    async writeFile(appDir, filePath, content) {
        const fullPath = path.join(appDir, filePath);
        await fs.writeFile(fullPath, content, 'utf8');
    }

    async getGenerationStatus(appId) {
        return this.generationStatus.get(appId) || { status: 'not_found' };
    }

    async downloadApp(appId) {
        const status = this.generationStatus.get(appId);
        if (!status || status.status !== 'completed') {
            throw new Error('App not ready for download');
        }

        const appDir = path.join(this.appsDir, appId);
        
        return new Promise((resolve, reject) => {
            const archive = archiver('zip', { zlib: { level: 9 } });
            const chunks = [];

            archive.on('data', chunk => chunks.push(chunk));
            archive.on('end', () => resolve(Buffer.concat(chunks)));
            archive.on('error', reject);

            archive.directory(appDir, false);
            archive.finalize();
        });
    }
}