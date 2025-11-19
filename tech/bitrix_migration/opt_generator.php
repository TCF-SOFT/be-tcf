#!/usr/bin/php
<?php
/**
 * Генерация прайс‑листа price_opt.xlsx
 * Оптовая цена = (розничная + супер‑оптовая) / 2, округление до 2‑х знаков.
 * Файл кладётся в /upload/sender/price/
 */

define('CHK_EVENT', true);               // корректная инициализация ядра из CLI
$_SERVER['DOCUMENT_ROOT'] = __DIR__ . '/..';
define('NO_KEEP_STATISTIC', true);
define('NOT_CHECK_PERMISSIONS', true);

require $_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_before.php';

ini_set('max_execution_time', 900);
ini_set('max_input_time',   900);
ini_set('memory_limit',     '512M');

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Worksheet\Table;
use PhpOffice\PhpSpreadsheet\Worksheet\Table\TableStyle;

\Bitrix\Main\Loader::includeModule('iblock');

/* ---------- Основной блок ---------- */

$sections     = getArSystem(26);   // все разделы каталога
$allSku       = getArSKU(28);      // весь склад
$items        = getArItem(26);     // родительские товары
$dataArray    = [];

$sectionWhiteList = [
    'mercedes', 'ford', 'masla_i_avtokhimiya', 'koreyskiy_avtoprom',
    'titan', 'kitayskiy_avtoprom', 'volkswagen'
];
$noSectionList = ['koreyskiy_avtoprom', 'kitayskiy_avtoprom', 'volkswagen'];

/* Формируем массив строк для Excel */
foreach ($sections as $secId => $section)
{
    if (!in_array($section['CODE'], $sectionWhiteList)) {
        continue;
    }

    if ($section['CODE'] === 'titan') {
        appendArSkuRaznoe($allSku, $sections, $items);
    } elseif (in_array($section['CODE'], $noSectionList)) {
        appendArSkuNoSection($allSku, $sections, $items);
    } else {
        appendArSku($allSku, $sections, $items);
    }

    $catalog  = $section['NAME'];
    $rows     = getCatalog($catalog, $allSku);   // строки для конкретного каталога
    usort($rows, 'sortSubSystem');
    $dataArray = array_merge($dataArray, $rows);
}

/* Сохраняем Excel */
$fileRelPath = '/upload/sender/price/price_opt.xlsx';
savePrice($fileRelPath, $dataArray);

/* ---------- Функции ---------- */

/**
 * Формирование excel‑файла
 */
function savePrice(string $fileName, array $dataArray): void
{
    $spreadsheet = new Spreadsheet();
    $sheet = $spreadsheet->getActiveSheet();

    /* Заголовок */
    $sheet->setCellValue('A1', 'ID')
      ->setCellValue('B1', 'Система')
      ->setCellValue('C1', 'Подсистема')
      ->setCellValue('D1', 'Название')
      ->setCellValue('E1', 'Бренд')
      ->setCellValue('F1', 'Номер производителя')
      ->setCellValue('G1', 'Кроссы')
      ->setCellValue('H1', 'Цена опт')
      ->setCellValue('I1', 'Цена розница')
      ->setCellValue('J1', 'Цена супер-опт')
      ->setCellValue('K1', 'Остаток')
      ->setCellValue('L1', 'bitrix_product_id')
      ->setCellValue('M1', 'bitrix_old_image');



    /* Данные */
    $sheet->fromArray($dataArray, null, 'A2');

    /* Оформляем таблицу */
    $table = new Table('A1:L' . (count($dataArray) + 1), 'PriceList');
    $table->getColumn('D')->setShowFilterButton(false);

    $style = new TableStyle();
    $style->setTheme(TableStyle::TABLE_STYLE_MEDIUM2)
          ->setShowRowStripes(true)
          ->setShowColumnStripes(true)
          ->setShowFirstColumn(true)
          ->setShowLastColumn(true);
    $table->setStyle($style);

    $sheet->addTable($table);

    /* Записываем файл */
    $writer = IOFactory::createWriter($spreadsheet, 'Xlsx');
    $writer->setPreCalculateFormulas(false);
    $writer->save($_SERVER['DOCUMENT_ROOT'] . $fileName);
}

/* Пользовательская сортировка для usort */
function sortSubSystem(array $a, array $b): int
{
    return $a[1] <=> $b[1] ?: $a[2] <=> $b[2] ?: $a[3] <=> $b[3] ?: $a[4] <=> $b[4];
}

/* --- вспомогательные append‑функции --- */

function appendArSku(array &$arSku, array $arSection, array $arItem): void
{
    foreach ($arSku as &$sku) {
        $parent        = $arItem[$sku['CML2_LINK']];
        $subsystemName = $arSection[$parent['SECTION_ID']]['NAME'];
        $subsystemPar  = $arSection[$parent['SECTION_ID']]['PARENT'];
        $systemName    = $arSection[$subsystemPar]['NAME'];
        $systemPar     = $arSection[$subsystemPar]['PARENT'];
        $catalogName   = $arSection[$systemPar]['NAME'];

        $sku['PARENT_XML_ID'] = $parent['XML_ID'];
        $sku['CROSS']     = $parent['CROSS'];
        $sku['SUBSYSTEM'] = $subsystemName;
        $sku['SYSTEM']    = $systemName;
        $sku['CATALOG']   = $catalogName;
    }
    unset($sku);
}

function appendArSkuRaznoe(array &$arSku, array $arSection, array $arItem): void
{
    foreach ($arSku as &$sku) {
        $parent       = $arItem[$sku['CML2_LINK']];
        $subsystemPar = $arSection[$parent['SECTION_ID']]['PARENT'];
        $systemPar    = $arSection[$subsystemPar]['PARENT'];
        $catalogName  = $arSection[$systemPar]['NAME'];

        $sku['PARENT_XML_ID'] = $parent['XML_ID'];
        $sku['CROSS']     = $parent['CROSS'];
        $sku['SUBSYSTEM'] = '';
        $sku['SYSTEM']    = '';
        $sku['CATALOG']   = $catalogName;
    }
    unset($sku);
}

function appendArSkuNoSection(array &$arSku, array $arSection, array $arItem): void
{
    foreach ($arSku as &$sku) {
        $parent         = $arItem[$sku['CML2_LINK']];
        $subsystemName  = $arSection[$parent['SECTION_ID']]['NAME'];

        $sku['PARENT_XML_ID'] = $parent['XML_ID'];
        $sku['CROSS']     = $parent['CROSS'];
        $sku['SUBSYSTEM'] = '';
        $sku['SYSTEM']    = '';
        $sku['CATALOG']   = $subsystemName;
    }
    unset($sku);
}

/**
 * Собирает строки для одного каталога
 */
function getCatalog(string $catalogName, array $arSku): array
{
    $out = [];
    foreach ($arSku as $sku) {
        if ($sku['CATALOG'] !== $catalogName || (int)$sku['QUANTITY'] < 0) {
            continue;
        }
        $out[] = [
            $sku['XML_ID'],                               // A: ID предложения
            $catalogName . '/' . $sku['SYSTEM'],          // B
            $sku['SUBSYSTEM'],                            // C
            $sku['NAME'],                                 // D
            $sku['VENDOR'],                               // E
            (string) $sku['ARTICLE'],                     // F
            (string) $sku['CROSS'],                       // G
            $sku['PRICE_OPT'],                            // H опт
            $sku['PRICE1'],                               // I розница
            $sku['PRICE2'],                               // J супер-опт
            $sku['QUANTITY'],                             // K остаток
            $sku['PARENT_XML_ID'],                        // L XML_ID товара
            $sku['IMAGE_PATH'],                           // M
        ];
    }
    return $out;
}

/* --- выборки из инфоблока --- */

/**
 * Все разделы: id => [CODE, NAME, PARENT]
 */
function getArSystem(int $iblockId): array
{
    $arSection = [];
    $rs = \CIBlockSection::GetList(
        ['NAME' => 'ASC'],
        ['=IBLOCK_ID' => $iblockId],
        false,
        ['IBLOCK_SECTION_ID', 'CODE', 'NAME', 'ID']
    );
    while ($s = $rs->Fetch()) {
        $arSection[$s['ID']] = [
            'CODE'   => $s['CODE'],
            'NAME'   => $s['NAME'],
            'PARENT' => $s['IBLOCK_SECTION_ID'],
        ];
    }
    return $arSection;
}

/**
 * SKU‑элементы: id => данные, включая PRICE_OPT
 */
function getArSKU(int $iblockId): array
{
    $result = [];
    $rs = \CIBlockElement::GetList(
        ['NAME' => 'ASC'],
        ['=IBLOCK_ID' => $iblockId],
        false,
        false,
        [
            'ID', 'XML_ID', 'NAME',
            'PROPERTY_CML2_LINK',
            'PROPERTY_ARTICLE',
            'PROPERTY_VENDOR',
            'CATALOG_PRICE_1',
            'CATALOG_PRICE_2',
            'CATALOG_QUANTITY',
            'DETAIL_PICTURE',
            'PREVIEW_PICTURE',
        ]
    );

    while ($el = $rs->Fetch()) {

        $price1 = (float) $el['CATALOG_PRICE_1'];
        $price2 = (float) $el['CATALOG_PRICE_2'];
        $priceOpt = round(($price1 + $price2) / 2);

        $imgId = $el['DETAIL_PICTURE'] ?: $el['PREVIEW_PICTURE'];
        $imgPath = CFile::GetPath($imgId);

        $result[$el['ID']] = [
            'XML_ID'     => $el['XML_ID'],
            'NAME'       => $el['NAME'],
            'CML2_LINK'  => $el['PROPERTY_CML2_LINK_VALUE'],
            'ARTICLE'    => $el['PROPERTY_ARTICLE_VALUE'],
            'VENDOR'     => $el['PROPERTY_VENDOR_VALUE'],
            'PRICE1'     => $price1,
            'PRICE2'     => $price2,
            'PRICE_OPT'  => $priceOpt,
            'QUANTITY'   => $el['CATALOG_QUANTITY'],
            'IMAGE_PATH' => $imgPath,
        ];
    }

    return $result;
}


/**
 * Родительские товары (для кроссов и названий)
 */
function getArItem(int $iblockId): array
{
    $result = [];
    $rs = \CIBlockElement::GetList(
        ['NAME' => 'ASC'],
        ['=IBLOCK_ID' => $iblockId],
        false,
        false,
        ['ID', 'XML_ID', 'NAME', 'PREVIEW_TEXT', 'IBLOCK_SECTION_ID']
    );
    while ($el = $rs->Fetch()) {
        $result[$el['ID']] = [
            'XML_ID'      => $el['XML_ID'],
            'NAME'        => $el['NAME'],
            'SECTION_ID'  => $el['IBLOCK_SECTION_ID'],
            'CROSS'       => $el['PREVIEW_TEXT'],
        ];
    }
    return $result;
}
