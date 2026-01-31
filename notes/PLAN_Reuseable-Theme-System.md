# Plan: Reusing MDviewer Multi-Theme System in Other PyQt Applications

## Overview

Extracts comprehensive multi-theme system from MDviewer to create a reusable, framework-agnostic theming solution for any Python PyQt application.

## Analysis of MDviewer Theme System

### Current Architecture Strengths
1. **Centralized Registry**: Single source of truth for theme definitions
2. **Data Classes**: Structured theme definitions with validation
3. **Dual-Layer Theming**: Separate UI (Fusion) and content themes
4. **Extensibility**: Easy to add new themes without code changes
5. **Backward Compatibility**: Graceful handling of legacy systems
6. **User-Friendly**: Category organization and live customization

### Core Components
1. **Theme Data Classes**: ThemeColors, UIPalette, Theme
2. **ThemeRegistry**: Central storage, validation, discovery
3. **UI Integration**: Dynamic menus, live switching
4. **Content Integration**: CSS generation, color management
5. **Settings Persistence**: Per-theme customization storage

## Extraction Strategy

### Phase 1: Core Framework Extraction

#### 1.1 Create Generic Theme Manager Package
**File**: theme_system/ (reusable package)

**Structure**:
```
theme_system/
├── __init__.py
├── core.py              # Core data classes
├── registry.py          # Theme registry
├── ui_themes.py        # UI theme definitions
├── content_themes.py   # Content theme definitions
├── validators.py        # Theme validation
└── utils.py            # Utility functions
```

**Core Data Classes** (core.py):
```python
@dataclass
class ThemeColors:
    """Content theme colors - 7 elements"""
    heading_color: str
    body_text_color: str
    background_color: str
    link_color: str
    blockquote_color: str
    code_bg_color: str
    border_color: str

@dataclass
class UIPalette:
    """UI palette colors - 8 elements"""
    window_color: str
    window_text_color: str
    base_color: str
    alternate_base_color: str
    text_color: str
    button_color: str
    button_text_color: str
    highlight_color: str
    highlighted_text_color: str

@dataclass
class Theme:
    """Complete theme definition"""
    name: str
    display_name: str
    content_colors: ThemeColors
    ui_palette: UIPalette
    description: str = ""
    is_built_in: bool = True
    category: str = "Custom"
```

#### 1.2 Framework-Agnostic Theme Registry
**File**: theme_system/registry.py

**Key Features**:
- Theme storage and validation
- Built-in theme initialization
- Custom theme registration
- Theme discovery from files/directories
- Category-based organization
- Import/export capabilities

```python
class ThemeRegistry:
    """Framework-agnostic theme registry"""
    
    def __init__(self, app_name: str = "Generic"):
        self.app_name = app_name
        self._themes: Dict[str, Theme] = {}
        self._theme_directories: List[str] = []
        self._load_builtin_themes()
        self._discover_custom_themes()
    
    def register_theme(self, theme: Theme) -> bool
    def get_theme(self, name: str) -> Optional[Theme]
    def get_all_themes(self) -> Dict[str, Theme]
    def get_themes_by_category(self, category: str) -> List[Theme]
    def remove_theme(self, name: str) -> bool
    def validate_theme(self, theme: Theme) -> bool
    def import_themes_from_directory(self, directory: str) -> int
    def export_theme(self, theme_name: str, file_path: str) -> bool
```

#### 1.3 UI Theme Abstraction
**File**: theme_system/ui_themes.py

**Current Issue**: MDviewer uses Qt Fusion style specifically

**Solution**: Create abstraction layer for multiple UI frameworks:

```python
class UIThemeEngine(ABC):
    """Abstract base for UI theme engines"""
    
    @abstractmethod
    def apply_theme(self, theme: Theme, app) -> None:
        """Apply UI theme to application"""

class QtFusionThemeEngine(UIThemeEngine):
    """Qt Fusion style theme engine"""
    
    def apply_theme(self, theme: Theme, app) -> None:
        palette = self._create_palette(theme.ui_palette)
        app.setPalette(palette)

class WebThemeEngine(UIThemeEngine):
    """Web application theme engine (for Flask/Django)"""
    
    def apply_theme(self, theme: Theme, app) -> None:
        css = self._generate_css(theme.ui_palette)
        # Apply to web framework
```

#### 1.4 Content Theme Integration
**File**: theme_system/content_themes.py

**Features**:
- CSS generation for multiple frameworks
- Markdown-aware styling
- Syntax highlighting themes
- Framework-agnostic color application

```python
class ContentThemeEngine:
    """Content theming for various content types"""
    
    def get_css_for_theme(self, theme: Theme, content_type: str = "markdown") -> str
    def apply_theme_to_widget(self, widget, theme: Theme) -> None
    def get_highlight_css(self, theme: Theme, syntax_engine: str) -> str
```

### Phase 2: Application Integration Framework

#### 2.1 Base Theme Manager
**File**: theme_system/base_manager.py

```python
class BaseThemeManager:
    """Base class for application-specific theme managers"""
    
    def __init__(self, app, theme_registry: ThemeRegistry):
        self.app = app
        self.registry = theme_registry
        self.current_theme = "default"
        self.ui_engine = self._create_ui_engine()
        self.content_engine = ContentThemeEngine()
        self.settings = self._get_settings()
    
    def switch_theme(self, theme_name: str) -> bool
    def get_available_themes(self) -> List[str]
    def apply_theme_to_ui(self, theme: Theme) -> None
    def apply_theme_to_content(self, theme: Theme) -> None
    def save_theme_settings(self) -> None
    def load_theme_settings(self) -> None
```

#### 2.2 PyQt Integration
**File**: theme_system/pyqt_integration.py

```python
class PyQtThemeManager(BaseThemeManager):
    """PyQt-specific theme manager"""
    
    def _create_ui_engine(self) -> UIThemeEngine:
        return QtFusionThemeEngine()
    
    def _get_settings(self) -> QSettings:
        return QSettings(self.app_name, self.app_name)
    
    def create_theme_menu(self, parent_widget) -> QMenu:
        """Create theme selection menu for PyQt applications"""
        
    def create_theme_dialog(self, parent_widget) -> QDialog:
        """Create theme customization dialog"""
        
    def setup_theme_shortcuts(self, parent_widget) -> None:
        """Setup keyboard shortcuts for theme switching"""
```

### Phase 3: Application-Specific Adaptation

#### 3.1 Application Template
**File**: theme_system/app_template.py

Provides template for integrating theme system:

```python
class ThemeApplication:
    """Template for theme-enabled applications"""
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.registry = ThemeRegistry(app_name)
        self.theme_manager = self._create_theme_manager()
        self._setup_themes()
    
    def _create_theme_manager(self):
        """Override in application for specific needs"""
        return PyQtThemeManager(self.app, self.registry)
    
    def _setup_themes(self):
        """Override to add application-specific themes"""
        pass
    
    def get_theme_manager(self):
        return self.theme_manager
```

## Implementation Plan

### Step 1: Extract Core Framework (Week 1)
1. **Create theme_system package** with core data classes
2. **Implement framework-agnostic registry** with validation
3. **Create UI theme engine abstraction** for multiple frameworks
4. **Build content theme engine** with CSS generation
5. **Add theme discovery system** for custom themes
6. **Create comprehensive tests** for core functionality

### Step 2: Build PyQt Integration (Week 2)
1. **Implement PyQt theme manager** with Fusion engine
2. **Create PyQt theme dialog** with live preview
3. **Build theme menu system** with category organization
4. **Add settings integration** for persistence
5. **Implement theme shortcuts** and toggles
6. **Test PyQt integration** thoroughly

### Step 3: Application Integration Kit (Week 3)
1. **Create application template** for easy integration
2. **Build integration guide** with step-by-step instructions
3. **Create
