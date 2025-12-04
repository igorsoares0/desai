# Interior AI API - Documentação para Android/Kotlin

## Sumário
- [Visão Geral](#visão-geral)
- [Base URL](#base-url)
- [Autenticação](#autenticação)
- [Endpoints](#endpoints)
  - [1. Redesign Interior](#1-redesign-interior)
  - [2. Design Exterior](#2-design-exterior)
  - [3. Garden Design](#3-garden-design)
  - [4. Reference Style](#4-reference-style)
  - [Endpoints de Listagem](#endpoints-de-listagem)
- [Modelos de Resposta](#modelos-de-resposta)
- [Tratamento de Erros](#tratamento-de-erros)
- [Exemplos Kotlin](#exemplos-kotlin)
- [Limitações e Custos](#limitações-e-custos)

---

## Visão Geral

A **Interior AI API** é uma API REST para redesign e design de ambientes usando inteligência artificial. Utiliza modelos avançados da Black Forest Labs (FLUX) via Replicate API.

**Recursos principais:**
- ✅ Redesign de interiores com fotorrealismo máximo
- ✅ Design de fachadas/exterior preservando estrutura arquitetônica
- ✅ Design de jardins e áreas externas
- ✅ Transferência de estilo usando imagem de referência
- ✅ 21 estilos diferentes disponíveis
- ✅ 9 tipos de cômodos suportados

---

## Base URL

```
http://SEU_SERVIDOR:8000
```

**Ambiente local:**
```
http://localhost:8000
```

**Produção:**
```
https://sua-api.com
```

---

## Autenticação

A API **não requer autenticação do cliente** (public API).

A autenticação com o Replicate é feita internamente via `REPLICATE_API_TOKEN` configurado no servidor.

---

## Endpoints

### 1. Redesign Interior

Transforma um ambiente interno aplicando um estilo específico com máximo fotorrealismo.

**Endpoint:** `POST /api/redesign-interior`

**Parâmetros (multipart/form-data):**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `image` | File | ✅ | Imagem do ambiente atual (JPG/PNG, max 10MB) |
| `style` | String | ✅ | Estilo desejado (ver lista de estilos) |
| `room_type` | String | ✅ | Tipo de cômodo (ver lista de room types) |
| `model` | String | ❌ | Modelo IA (default: "flux-dev") |

**Exemplo de Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/redesign-interior" \
  -F "image=@sala.jpg" \
  -F "style=modern" \
  -F "room_type=living_room" \
  -F "model=flux-dev"
```

**Resposta de Sucesso (200 OK):**
```json
{
  "success": true,
  "output_url": "https://replicate.delivery/pbxt/abc123.jpg",
  "style": "modern",
  "room_type": "living_room",
  "model_used": "flux-dev",
  "processing_time": 28.5
}
```

**Detalhes técnicos:**
- Usa `strength` fixo de **0.6** para balancear realismo
- **35 steps** de inferência para alta qualidade
- **Guidance scale 9.5** para fidelidade ao prompt
- Imagens otimizadas automaticamente para 1024px

---

### 2. Design Exterior

Aplica novo estilo arquitetônico à fachada/exterior **preservando 100% da estrutura** da casa.

**Endpoint:** `POST /api/design-exterior`

**Parâmetros (multipart/form-data):**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `image` | File | ✅ | Imagem da fachada atual (JPG/PNG, max 10MB) |
| `style` | String | ✅ | Estilo arquitetônico desejado |
| `model` | String | ❌ | Modelo IA (default: "flux-canny-pro") |

**Exemplo de Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/design-exterior" \
  -F "image=@casa.jpg" \
  -F "style=mediterranean" \
  -F "model=flux-canny-pro"
```

**Resposta de Sucesso (200 OK):**
```json
{
  "success": true,
  "output_url": "https://replicate.delivery/pbxt/xyz789.jpg",
  "style": "mediterranean",
  "room_type": null,
  "model_used": "flux-canny-pro",
  "processing_time": 45.2
}
```

**Detalhes técnicos:**
- Usa **FLUX.1 Canny Pro** com ControlNet + Canny edge detection
- Detecta automaticamente contornos da estrutura (paredes, janelas, portas)
- **Guidance 50** (máximo) para preservação rígida da estrutura
- **40 steps** para qualidade profissional
- **Mantém 100% da arquitetura**, muda apenas estilo/materiais

---

### 3. Garden Design

Design de jardins e áreas externas com máximo fotorrealismo.

**Endpoint:** `POST /api/garden-design`

**Parâmetros (multipart/form-data):**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `image` | File | ✅ | Imagem do jardim/área atual (JPG/PNG, max 10MB) |
| `style` | String | ✅ | Estilo de jardim desejado |
| `garden_type` | String | ❌ | Tipo de área (default: "garden") |
| `strength` | Float | ❌ | Força transformação 0.0-1.0 (default: 0.35) |
| `model` | String | ❌ | Modelo IA (default: "flux-dev") |

**Garden Types disponíveis:**
- `garden` - Jardim geral
- `backyard` - Quintal
- `front_yard` - Jardim frontal
- `patio` - Pátio
- `terrace` - Terraço
- `rooftop` - Cobertura/Rooftop

**Exemplo de Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/garden-design" \
  -F "image=@jardim.jpg" \
  -F "style=japanese_design" \
  -F "garden_type=backyard" \
  -F "strength=0.35"
```

**Resposta de Sucesso (200 OK):**
```json
{
  "success": true,
  "output_url": "https://replicate.delivery/pbxt/garden123.jpg",
  "style": "japanese_design",
  "room_type": "backyard",
  "model_used": "flux-dev",
  "processing_time": 32.1
}
```

**Detalhes técnicos:**
- **Strength 0.35** (padrão) para máximo fotorrealismo
- **Guidance 15.0** para forçar fotorrealismo
- Prompt otimizado para fotografia real de jardim

---

### 4. Reference Style

Transferência de estilo usando uma imagem de referência (style transfer).

**Endpoint:** `POST /api/reference-style`

**Parâmetros (multipart/form-data):**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `base_image` | File | ✅ | Imagem do ambiente base (JPG/PNG, max 10MB) |
| `reference_image` | File | ✅ | Imagem de referência de estilo (JPG/PNG, max 10MB) |
| `room_type` | String | ✅ | Tipo de cômodo |
| `strength` | Float | ❌ | Força transformação 0.0-1.0 (default: 0.6) |
| `style_weight` | Float | ❌ | Peso do estilo ref 0.0-1.0 (default: 0.7) |
| `model` | String | ❌ | Modelo IA (default: "flux-dev") |

**Exemplo de Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/reference-style" \
  -F "base_image=@minha_sala.jpg" \
  -F "reference_image=@inspiracao.jpg" \
  -F "room_type=living_room" \
  -F "strength=0.6" \
  -F "style_weight=0.7"
```

**Resposta de Sucesso (200 OK):**
```json
{
  "success": true,
  "output_url": "https://replicate.delivery/pbxt/ref456.jpg",
  "style": "reference_style",
  "room_type": "living_room",
  "model_used": "flux-dev",
  "processing_time": 38.7
}
```

---

### Endpoints de Listagem

#### GET /api/styles
Retorna lista completa de estilos disponíveis.

**Response:**
```json
{
  "styles": [
    {"id": "modern", "name": "Moderno", "description": "Linhas limpas e cores neutras"},
    {"id": "minimalist", "name": "Minimalista", "description": "Simples e despojado"},
    {"id": "scandinavian", "name": "Escandinavo", "description": "Aconchegante e natural"},
    ...
  ]
}
```

#### GET /api/room-types
Retorna lista de tipos de cômodos.

**Response:**
```json
{
  "room_types": [
    {"id": "living_room", "name": "Sala de Estar"},
    {"id": "bedroom", "name": "Quarto"},
    {"id": "kitchen", "name": "Cozinha"},
    ...
  ]
}
```

#### GET /api/garden-types
Retorna lista de tipos de jardim/área externa.

**Response:**
```json
{
  "garden_types": [
    {"id": "garden", "name": "Jardim"},
    {"id": "backyard", "name": "Quintal"},
    {"id": "patio", "name": "Pátio"},
    ...
  ]
}
```

#### GET /api/models
Retorna modelos de IA disponíveis.

**Response:**
```json
{
  "models": [
    {
      "id": "flux-schnell",
      "name": "Flux Schnell",
      "description": "Rápido e eficiente",
      "speed": "10-15s",
      "cost": "$0.001"
    },
    {
      "id": "flux-dev",
      "name": "Flux Dev",
      "description": "Alta qualidade (RECOMENDADO)",
      "speed": "25-35s",
      "cost": "$0.003"
    },
    {
      "id": "flux-canny-pro",
      "name": "Flux Canny Pro",
      "description": "Edge detection para preservar estrutura (EXTERIOR)",
      "speed": "45-50s",
      "cost": "$0.05"
    }
  ]
}
```

#### GET /health
Verifica saúde da API.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "replicate_configured": true
}
```

---

## Modelos de Resposta

### GenerateResponse (Sucesso)
```json
{
  "success": true,
  "output_url": "https://replicate.delivery/pbxt/...",
  "style": "modern",
  "room_type": "living_room",
  "model_used": "flux-dev",
  "processing_time": 28.5
}
```

### GenerateResponse (Erro)
```json
{
  "success": false,
  "output_url": null,
  "style": null,
  "room_type": null,
  "model_used": null,
  "processing_time": 2.3,
  "error": "Imagem muito grande. Máximo permitido: 10.0MB"
}
```

---

## Tratamento de Erros

### Códigos HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Bad Request (parâmetros inválidos) |
| 422 | Unprocessable Entity (validação falhou) |
| 500 | Internal Server Error |

### Erros Comuns

**Imagem muito grande:**
```json
{
  "success": false,
  "error": "Imagem muito grande. Máximo permitido: 10.0MB"
}
```

**Arquivo inválido:**
```json
{
  "success": false,
  "error": "Arquivo inválido: cannot identify image file"
}
```

**Token não configurado:**
```json
{
  "detail": "REPLICATE_API_TOKEN não configurado"
}
```

---

## Exemplos Kotlin

### 1. Setup - Dependências (build.gradle.kts)

```kotlin
dependencies {
    // OkHttp para requisições HTTP
    implementation("com.squareup.okhttp3:okhttp:4.12.0")

    // Gson para parsing JSON
    implementation("com.google.code.gson:gson:2.10.1")

    // Coroutines para async
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
```

### 2. Modelos de Dados

```kotlin
data class GenerateResponse(
    val success: Boolean,
    val output_url: String?,
    val style: String?,
    val room_type: String?,
    val model_used: String?,
    val processing_time: Float?,
    val error: String?
)

data class StyleItem(
    val id: String,
    val name: String,
    val description: String
)

data class StylesResponse(
    val styles: List<StyleItem>
)
```

### 3. API Client Class

```kotlin
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.IOException

class InteriorAIClient(private val baseUrl: String = "http://localhost:8000") {

    private val client = OkHttpClient()
    private val gson = Gson()

    /**
     * Redesign de interior
     */
    suspend fun redesignInterior(
        imageFile: File,
        style: String,
        roomType: String,
        model: String = "flux-dev"
    ): GenerateResponse = withContext(Dispatchers.IO) {

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "image",
                imageFile.name,
                RequestBody.create("image/*".toMediaTypeOrNull(), imageFile)
            )
            .addFormDataPart("style", style)
            .addFormDataPart("room_type", roomType)
            .addFormDataPart("model", model)
            .build()

        val request = Request.Builder()
            .url("$baseUrl/api/redesign-interior")
            .post(requestBody)
            .build()

        val response = client.newCall(request).execute()
        val responseBody = response.body?.string() ?: throw IOException("Empty response")

        gson.fromJson(responseBody, GenerateResponse::class.java)
    }

    /**
     * Design de exterior (preserva estrutura)
     */
    suspend fun designExterior(
        imageFile: File,
        style: String,
        model: String = "flux-canny-pro"
    ): GenerateResponse = withContext(Dispatchers.IO) {

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "image",
                imageFile.name,
                RequestBody.create("image/*".toMediaTypeOrNull(), imageFile)
            )
            .addFormDataPart("style", style)
            .addFormDataPart("model", model)
            .build()

        val request = Request.Builder()
            .url("$baseUrl/api/design-exterior")
            .post(requestBody)
            .build()

        val response = client.newCall(request).execute()
        val responseBody = response.body?.string() ?: throw IOException("Empty response")

        gson.fromJson(responseBody, GenerateResponse::class.java)
    }

    /**
     * Design de jardim
     */
    suspend fun designGarden(
        imageFile: File,
        style: String,
        gardenType: String = "garden",
        strength: Float = 0.35f,
        model: String = "flux-dev"
    ): GenerateResponse = withContext(Dispatchers.IO) {

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "image",
                imageFile.name,
                RequestBody.create("image/*".toMediaTypeOrNull(), imageFile)
            )
            .addFormDataPart("style", style)
            .addFormDataPart("garden_type", gardenType)
            .addFormDataPart("strength", strength.toString())
            .addFormDataPart("model", model)
            .build()

        val request = Request.Builder()
            .url("$baseUrl/api/garden-design")
            .post(requestBody)
            .build()

        val response = client.newCall(request).execute()
        val responseBody = response.body?.string() ?: throw IOException("Empty response")

        gson.fromJson(responseBody, GenerateResponse::class.java)
    }

    /**
     * Reference style transfer
     */
    suspend fun referenceStyle(
        baseImageFile: File,
        referenceImageFile: File,
        roomType: String,
        strength: Float = 0.6f,
        styleWeight: Float = 0.7f,
        model: String = "flux-dev"
    ): GenerateResponse = withContext(Dispatchers.IO) {

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "base_image",
                baseImageFile.name,
                RequestBody.create("image/*".toMediaTypeOrNull(), baseImageFile)
            )
            .addFormDataPart(
                "reference_image",
                referenceImageFile.name,
                RequestBody.create("image/*".toMediaTypeOrNull(), referenceImageFile)
            )
            .addFormDataPart("room_type", roomType)
            .addFormDataPart("strength", strength.toString())
            .addFormDataPart("style_weight", styleWeight.toString())
            .addFormDataPart("model", model)
            .build()

        val request = Request.Builder()
            .url("$baseUrl/api/reference-style")
            .post(requestBody)
            .build()

        val response = client.newCall(request).execute()
        val responseBody = response.body?.string() ?: throw IOException("Empty response")

        gson.fromJson(responseBody, GenerateResponse::class.java)
    }

    /**
     * Buscar lista de estilos
     */
    suspend fun getStyles(): StylesResponse = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("$baseUrl/api/styles")
            .get()
            .build()

        val response = client.newCall(request).execute()
        val responseBody = response.body?.string() ?: throw IOException("Empty response")

        gson.fromJson(responseBody, StylesResponse::class.java)
    }

    /**
     * Health check
     */
    suspend fun healthCheck(): Boolean = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/health")
                .get()
                .build()

            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }
}
```

### 4. Uso em Activity/Fragment

```kotlin
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import java.io.File

class MainActivity : AppCompatActivity() {

    private val apiClient = InteriorAIClient("http://sua-api.com")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Exemplo: Redesign de sala
        findViewById<Button>(R.id.btnRedesign).setOnClickListener {
            redesignRoom()
        }
    }

    private fun redesignRoom() {
        lifecycleScope.launch {
            try {
                // Mostrar loading
                showLoading(true)

                // Arquivo de imagem (ex: da galeria ou câmera)
                val imageFile = File(cacheDir, "room_photo.jpg")

                // Fazer request
                val response = apiClient.redesignInterior(
                    imageFile = imageFile,
                    style = "modern",
                    roomType = "living_room"
                )

                // Processar resposta
                if (response.success && response.output_url != null) {
                    // Carregar imagem gerada (ex: usando Glide ou Coil)
                    loadImage(response.output_url)

                    Toast.makeText(
                        this@MainActivity,
                        "Gerado em ${response.processing_time}s",
                        Toast.LENGTH_SHORT
                    ).show()
                } else {
                    Toast.makeText(
                        this@MainActivity,
                        "Erro: ${response.error}",
                        Toast.LENGTH_LONG
                    ).show()
                }

            } catch (e: Exception) {
                Toast.makeText(
                    this@MainActivity,
                    "Erro: ${e.message}",
                    Toast.LENGTH_LONG
                ).show()
            } finally {
                showLoading(false)
            }
        }
    }

    private fun showLoading(show: Boolean) {
        // Mostrar/esconder progress bar
    }

    private fun loadImage(url: String) {
        // Carregar imagem usando Glide, Coil, Picasso, etc
        // Glide.with(this).load(url).into(imageView)
    }
}
```

### 5. ViewModel Pattern (Recomendado)

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.io.File

sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Success(val imageUrl: String, val processingTime: Float) : UiState()
    data class Error(val message: String) : UiState()
}

class InteriorViewModel : ViewModel() {

    private val apiClient = InteriorAIClient("http://sua-api.com")

    private val _uiState = MutableStateFlow<UiState>(UiState.Idle)
    val uiState: StateFlow<UiState> = _uiState

    fun redesignInterior(imageFile: File, style: String, roomType: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val response = apiClient.redesignInterior(imageFile, style, roomType)

                if (response.success && response.output_url != null) {
                    _uiState.value = UiState.Success(
                        response.output_url,
                        response.processing_time ?: 0f
                    )
                } else {
                    _uiState.value = UiState.Error(response.error ?: "Erro desconhecido")
                }

            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Erro de conexão")
            }
        }
    }

    fun designExterior(imageFile: File, style: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val response = apiClient.designExterior(imageFile, style)

                if (response.success && response.output_url != null) {
                    _uiState.value = UiState.Success(
                        response.output_url,
                        response.processing_time ?: 0f
                    )
                } else {
                    _uiState.value = UiState.Error(response.error ?: "Erro desconhecido")
                }

            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Erro de conexão")
            }
        }
    }
}
```

### 6. Observar State em Compose (Jetpack Compose)

```kotlin
@Composable
fun InteriorScreen(viewModel: InteriorViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    when (val state = uiState) {
        is UiState.Idle -> {
            // Mostrar tela inicial
        }
        is UiState.Loading -> {
            CircularProgressIndicator()
        }
        is UiState.Success -> {
            AsyncImage(
                model = state.imageUrl,
                contentDescription = "Generated room"
            )
            Text("Processado em ${state.processingTime}s")
        }
        is UiState.Error -> {
            Text("Erro: ${state.message}", color = Color.Red)
        }
    }
}
```

---

## Limitações e Custos

### Limites
- **Tamanho máximo da imagem:** 10MB
- **Formatos suportados:** JPG, PNG
- **Resolução otimizada:** 1024x1024px (redimensionada automaticamente)
- **Timeout:** Requests podem levar de 10s a 60s dependendo do modelo

### Custos (via Replicate API)

| Modelo | Custo por geração | Tempo médio |
|--------|------------------|-------------|
| flux-schnell | $0.001 | 10-15s |
| flux-dev | $0.003 | 25-35s |
| flux-canny-pro | $0.05 | 45-50s |

**Nota:** Custos são aproximados e podem variar. O servidor deve ter créditos configurados na conta Replicate.

### Recomendações

1. **Interior Design:** Use `flux-dev` (melhor custo-benefício)
2. **Exterior Design:** Use `flux-canny-pro` (preserva estrutura)
3. **Garden Design:** Use `flux-dev` com strength baixo (0.35)
4. **Reference Style:** Use `flux-dev`

---

## Suporte

Para questões técnicas ou bugs, entre em contato com a equipe de desenvolvimento.

**Versão da API:** 2.0.0
**Última atualização:** Dezembro 2024
